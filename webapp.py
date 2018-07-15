from exts import create_app, db, down_report, auto_check
from models import User, Host, History
from sqlalchemy import distinct
from decorators import login_required
from flask import request, session, jsonify
from flask import render_template, redirect, url_for, send_from_directory
app = create_app()
status = {}
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


# 主页面
@app.route('/')
@login_required
def index():
    return render_template('index.html')


# 修改密码页面
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


# 例检主页面
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


# 例检单台主机页面
@app.route('/check/info/')
@login_required
def check_host():
    name = request.args.get('name')
    hosts_temp = Host.query.filter(Host.cluster == name).all()
    hosts = [x.hostname for x in hosts_temp]
    return render_template('check_host.html', name=name, hosts=hosts)


# 例检确认页面
@app.route('/check/lj_check/')
@login_required
def lj():
    clustename = request.args.get('clustename', None)
    hostname = request.args.get('hostname', None)
    if clustename:
        result = clustename
        host_type = "jq"
    else:
        result = hostname
        host_type = "zj"
    return render_template('lj_result.html', result=result, type=host_type)


# 自动例检主函数
@app.route('/check/autocheck', methods=['GET', 'POST'])
def autocheck_run():
    import datetime
    hostname = request.form.get('hostname')
    type = request.form.get('type')
    seed = request.form.get("seed")
    status[seed] = 20
    flag = "success"
    # flag = auto_check(type,hostname)
    status[seed] =80
    # report_name = down_report()
    report_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 例检成功，添加到历史记录
    if flag == "success":
        new_type = "集群" if type == "jq" else "主机"
        add_log = History(checktime=report_name, hostname=hostname, type=new_type)
        db.session.add(add_log)
        db.session.commit()
    status[seed] = 100
    status.pop(seed)
    return jsonify({'flag':flag,'filename':report_name})



# 获取例检状态,实现前端进度条
@app.route('/check/autocheck_status/<id>', methods=['GET', 'POST'])
def autocheck_status(id):
    seed = request.form.get("seed")
    # print(seed)
    # print(status.get(seed))
    return str(status.get(seed))


# 下载例检报告
@app.route('/download/<file>')
def download(file):
    filepath = 'backup/' + str(file) + '/'
    filename = str(file) + ".tar.gz"
    return send_from_directory(filepath, filename, as_attachment=True)


# 例检配置
@app.route('/check/setting')
@login_required
def check_setting():

    # datas = db.session.query(Host).all()
    class_type = ['One','Two','Three','Four','Five','Six', 'Seven','Eight','Nine','Ten','Eleven','Twelve']
    datas = []
    cluste_type = db.session.query(distinct(Host.type)).all()
    types = [x[0] for x in cluste_type]
    for i, c_type in enumerate(types):
        cluste_temps = db.session.query(Host).filter(Host.type == c_type).all()
        # print(cluste_temps)
        # clusters = [x[0] for x in cluste_temps]
        datas.append((c_type, cluste_temps,class_type[i]))
    return render_template('check_setting.html',datas=datas)
    # print(datas)
    # return "测试"


# 添加例检项
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
    try:
        db.session.commit()
        return "success"
    except:
        return "fail"


# 删除例检项,暂未实现
@app.route('/check/setting/del')
@login_required
def check_del():
    print(request.args)
    print(request.form.get('del_host'))
    return render_template('check_del.html')


# 话单查询页面,暂未实现
@app.route('/query')
@login_required
def query():
    return render_template('query.html')


@app.route('/history')
@login_required
def history():
    # 获取get请求传过来的页数,没有传参数，默认为1
    page = int(request.args.get('page', 1))
    # datas = db.session.query(History).all()
    paginate = History.query.order_by(History.id.asc()).paginate(page, per_page=10, error_out=False)
    datas =  paginate.items
    return render_template("history.html",paginate=paginate, datas=datas)


# 上下文管理器，返回的结果会作为变量在所有模板中进行渲染
@app.context_processor
def my_context_processor():
    username = session.get('username')
    if username:
        return {'username': username}
    else:
        return {'username': None}


if __name__ == '__main__':
    # 开启flask的多线程
    app.run(host='0.0.0.0', threaded=True)
