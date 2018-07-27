import datetime
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
    # 获取caps数据
    datas = db.session.execute("select `date`,`scpas_caps`,`catas_caps` from caps",
                               bind=db.get_engine(app, bind="tongji")).fetchall()
    date = [int(x[0]) for x in datas]
    scpas_caps = [x[1] for x in datas]
    catas_caps = [x[2] for x in datas]
    # 获取用户数据
    user_datas = db.session.execute("select vpmn_volte,hjh_volte,pyq_volte,crbt_volte from users order by date desc",
                                    bind=db.get_engine(app, bind="tongji")).fetchone()
    v_users = int(user_datas[0]) + int(user_datas[1]) + int(user_datas[2])
    v_total = 15000000
    v_per = format(v_users/v_total, '.2%')
    c_users = int(user_datas[3])
    c_total = 8500000
    c_per = format(c_users/c_total, '.2%')
    # 获取cpu等性能数据
    # date1="20180709"
    # date2="20180708"
    date1 = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y%m%d")
    date2 = (datetime.datetime.today() - datetime.timedelta(2)).strftime("%Y%m%d")
    # 近两天CPU数据
    cpu_temp = db.session.execute("select `cluste`,`max_cpu` from as_pfmc where date={}".format(date1),
                                  bind=db.get_engine(app, bind="tongji")).fetchall()
    cluster = [x[0] for x in cpu_temp]
    cpu_date1 = [x[1] for x in cpu_temp]
    cpu_temp2 = db.session.execute("select `max_cpu` from as_pfmc where date={}".format(date2),
                                   bind=db.get_engine(app, bind="tongji")).fetchall()
    cpu_date2 = [x[0] for x in cpu_temp2]
    # 近两天内存数据
    mem_temp1 = db.session.execute("select `max_mem` from as_pfmc where date={}".format(date1),
                                  bind=db.get_engine(app, bind="tongji")).fetchall()
    mem_date1 = [x[0] for x in mem_temp1]
    mem_temp2 = db.session.execute("select `max_mem` from as_pfmc where date={}".format(date2),
                                  bind=db.get_engine(app, bind="tongji")).fetchall()
    mem_date2 = [x[0] for x in mem_temp2]

    io_temp1 = db.session.execute("select `max_io` from as_pfmc where date={}".format(date1),
                                  bind=db.get_engine(app, bind="tongji")).fetchall()
    io_date1 = [x[0] for x in io_temp1]
    io_temp2 = db.session.execute("select `max_io` from as_pfmc where date={}".format(date2),
                                  bind=db.get_engine(app, bind="tongji")).fetchall()
    io_date2 = [x[0] for x in io_temp2]
    # 获取最近例检记录
    paginate = History.query.order_by(History.id.desc()).paginate(1, per_page=8, error_out=False)
    lj_datas = paginate.items
    return render_template('index.html',**locals())

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
    return render_template('check.html', data=data)


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
    hostname = request.form.get('hostname')
    host_type = request.form.get('type')
    seed = request.form.get("seed")
    status[seed] = 20
    try:
        flag = auto_check(host_type, hostname)
    except:
        flag = "fail"
    status[seed] = 80
    # 例检成功，添加到历史记录
    if flag == "success":
        report_name = down_report()
        new_type = "集群" if host_type == "jq" else "主机"
        add_log = History(checktime=report_name, hostname=hostname, type=new_type)
        db.session.add(add_log)
        db.session.commit()
    else:
        report_name = "null"
    status[seed] = 100
    status.pop(seed)
    return jsonify({'flag': flag, 'filename': report_name})


# 获取例检状态,实现前端进度条
@app.route('/check/autocheck_status/<id>', methods=['GET', 'POST'])
def autocheck_status(id):
    seed = request.form.get("seed")
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
    # 匹配对应的css样式
    class_type = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve']
    datas = []
    cluste_type = db.session.query(distinct(Host.type)).all()
    types = [x[0] for x in cluste_type]
    for i, c_type in enumerate(types):
        cluste_temps = db.session.query(Host).filter(Host.type == c_type).all()
        datas.append((c_type, cluste_temps, class_type[i]))
    return render_template('check_setting.html', datas=datas)


# 添加例检项
@app.route('/check/setting/add', methods=['GET', 'POST'])
@login_required
def check_add():
    host_type = request.form.get('type')
    cluster = request.form.get('cluster')
    hosts_temp = request.form.get('hostname')
    hosts = hosts_temp.split('|')
    for host in hosts:
        add_host = Host(type=host_type, cluster=cluster, hostname=host)
        db.session.add(add_host)
    try:
        db.session.commit()
        return "success"
    except:
        return "fail"


# 删除例检项
@app.route('/check/setting/del', methods=['GET', 'POST'])
@login_required
def check_del():
    del_ids = request.form.get('del_id')
    if not del_ids:
        return "fail"
    ids = del_ids.split(",")
    for del_id in ids:
        # 判定是否为空或者非数字
        if del_id and del_id.isdigit():
            to_del_id = Host.query.filter(Host.id == del_id).first()
            db.session.delete(to_del_id)
        db.session.commit()
    return "success"


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
    paginate = History.query.order_by(History.id.asc()).paginate(page, per_page=10, error_out=False)
    datas = paginate.items
    return render_template("history.html", paginate=paginate, datas=datas)


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
    app.run(host='0.0.0.0',threaded=True)
