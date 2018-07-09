from collections import namedtuple
from exts import create_app, db
from models import User, Host
from sqlalchemy import distinct
from decorators import login_required
from flask import request, session
from flask import render_template, redirect, url_for
app = create_app()


# 默认的视图函数，只能采用get请求，需要使用post，需要说明
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
        return render_template('login.html', error=error)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        result = User.query.filter(User.username == username).first()
        if result:
            if password == result.password:
                session['username'] = username
                session.permanent = True
                return redirect(url_for('index'))
            else:
                error = "密码错误！"
                return render_template('login.html', error=error)
        else:
            error = "账号{}不存在！".format(username)
            return render_template('login.html', error=error)

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/user/')
def user():
    return render_template('user.html')


@app.route('/check/')
@login_required
def check():
    data = []
    cluste_type = db.session.query(distinct(Host.type)).all()
    types = [x[0] for x in cluste_type]
    for type in types:
        cluste_temps = Host.query.filter(Host.type == type).all()
        clusters = [x.cluster for x in cluste_temps]
        data.append((type,clusters))
    print(data)
    return render_template('check.html',data=data)


@app.route('/check/info/')
@login_required
def check_host():
    name = request.args.get('name')
    hosts_temp = Host.query.filter(Host.cluster == name).all()
    hosts = [x.hostname for x in hosts_temp]
    return render_template('check_host.html', name=name, hosts=hosts)


@app.route('/check/lj/')
@login_required
def auto_check():
    name = request.args.get('name')
    return "调用自动例检接口，参数值{}".format(name)


@app.route('/check/setting/')
@login_required
def check_setting():
    return render_template('check_setting.html')


@app.route('/check/setting/add/')
@login_required
def check_add():
    return render_template('check_add.html')


@app.route('/check/setting/del/')
@login_required
def check_del():
    return render_template('check_del.html')


@app.route('/query/')
@login_required
def query():
    return render_template('query.html')


# 上下文管理器，返回的结果会作为变量在所有模板中进行渲染
@app.context_processor
def my_context_processor():
    username = session.get('username')
    if username:
        return {'username' : username}
    else:
        return {'username' : None}


if __name__ == '__main__':
    app.run()
