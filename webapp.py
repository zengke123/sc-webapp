from exts import create_app, db, auto_check
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    error = None
    if request.method == 'GET':
        return render_template('user.html', error=error)
    else:
        username = session.get('username')
        oldpassword = request.form.get('oldpassword')
        newpassword1 = request.form.get('newpassword1')
        newpassword2 = request.form.get('newpassword2')
        result = User.query.filter(User.username == username).first()
        if result:
            if oldpassword == result.password:
                if newpassword1 == newpassword2:
                    result.password = newpassword2
                    db.session.commit()
                    error = "密码修改成功！"
                else:
                    error = "两次输入密码不一致！"
            else:
                error = "原密码输入错误！"
    return render_template('user.html', error=error)


@app.route('/check')
@login_required
def check():
    data = []
    cluste_type = db.session.query(distinct(Host.type)).all()
    types = [x[0] for x in cluste_type]
    for c_type in types:
        # cluste_temps = Host.query.filter(Host.type == type).distinct().all()
        cluste_temps = db.session.query(distinct(Host.cluster)).filter(Host.type == c_type).all()
        clusters = [x[0] for x in cluste_temps]
        data.append((c_type, clusters))
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
def lj():
    clustename = request.args.get('clustename', None)
    hostname = request.args.get('hostname', None)
    if clustename:
        result = auto_check(lj_type='jq', name=clustename)
        # return "调用集群自动例检接口，参数值{}".format(clustename)
    else:
        result = auto_check(lj_type='zj', name=hostname)
        # return "调用主机自动例检接口，参数值{}".format(hostname)
    return result

@app.route('/check/setting')
@login_required
def check_setting():

    # datas = db.session.query(Host).all()
    class_type = ['One','Two','Three','Four','Five','Six', 'Seven','Eight','Nine','Ten','Eleven','Twelve']
    datas = []
    cluste_type = db.session.query(distinct(Host.type)).all()
    types = [x[0] for x in cluste_type]
    nums = len(types)
    for i, c_type in enumerate(types):
        cluste_temps = db.session.query(Host).filter(Host.type == c_type).all()
        print(cluste_temps)
        # clusters = [x[0] for x in cluste_temps]
        datas.append((c_type, cluste_temps,class_type[i]))
    return render_template('check_setting.html',datas=datas)
    # print(datas)
    # return "测试"

@app.route('/check/setting/add/', methods=['GET', 'POST'])
@login_required
def check_add():
    type = request.form.get('type')
    cluster = request.form.get('cluster')
    hosts_temp = request.form.get('hostname')
    hosts = hosts_temp.split('|')
    for host in hosts:
        add_host = Host(type=type, cluster=cluster, hostname=host)
        db.session.add(add_host)
    db.session.commit()
    # return render_template('check_add.html')
    return "添加成功"

@app.route('/check/setting/del')
@login_required
def check_del():
    return render_template('check_del.html')


@app.route('/query')
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
