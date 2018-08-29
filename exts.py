from web_init import db
from models import History, Host, Jobs


def auto_check(lj_type, name):
    import pexpect
    username = "root"
    password = '123456'
    cmd = 'zj zjlj lj:type={},name={}'.format(lj_type, name)
    child = pexpect.spawn('telnet 0 47303', timeout=300)
    child.expect('login:')
    child.sendline(username)
    child.expect('password:')
    child.sendline(password)
    child.expect('root > ')
    child.sendline(cmd)
    child.expect('{}root >')
    result = child.before
    if b'RETN=0000' in result:
        flag = "success"
    else:
        flag = "fail"
    child.sendline('quit')
    child.close()
    return flag


def auto_check2(lj_type, name):
    import time
    cmd = 'zj zjlj lj:type={},name={}'.format(lj_type, name)
    print(cmd)
    time.sleep(4)
    return "success"
    # print(flag)


def down_report():
    import datetime
    import os
    name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    src_path = "/home/omscc/zengke/output/*"
    dst_path = "/home/omscc/webapp/backup" + os.sep + str(name)
    os.mkdir(dst_path)
    cp_cmd = "cp -R {} {}".format(src_path, dst_path)
    os.system(cp_cmd)
    os.environ['name'] = str(name)
    tmd_cmd = "tar zcf ${name}.tar.gz * --remove-files;rm -rf host"
    os.chdir(dst_path)
    os.system(tmd_cmd)
    return str(name)


def add_check_log(host_type, hostname):
    report_name = down_report()
    new_type = "集群" if host_type == "jq" else "主机"
    add_log = History(checktime=report_name, hostname=hostname, type=new_type)
    db.session.add(add_log)
    db.session.commit()


def schedule_check(items, hosts, clusters):
    import time
    from collections import namedtuple
    CheckItem = namedtuple("CheckItem","type name")
    temp_items = items.split(",")
    check_items =[]
    for item in temp_items:
        if item in hosts:
            check_items.append(CheckItem(type="zj",name=item))
        elif item in clusters:
            check_items.append(CheckItem(type="jq", name=item))
    for item in check_items:
        flag = auto_check(item.type, item.name)
        if flag == "success":
            #add_check_log(item.type, item.name)
            # 入库
            print("scheduler任务例检【{}】【{}】成功".format(item.type, item.name))
        else:
            print("scheduler任务例检【{}】【{}】失败".format(item.type, item.name))
        time.sleep(30)


def test_check(items, hosts, clusters):
    import time, datetime
    from collections import namedtuple
    CheckItem = namedtuple("CheckItem","type name")
    temp_items = items.split(",")
    check_items =[]
    for item in temp_items:
        if item in hosts:
            check_items.append(CheckItem(type="zj",name=item))
        elif item in clusters:
            check_items.append(CheckItem(type="jq", name=item))
        else:
            print("数据异常")
            # 抛出异常 raise
    for item in check_items:
        print(datetime.datetime.now(), "例检 {} {}".format(item.type,item.name))
        time.sleep(5)
        print(datetime.datetime.now(), "例检完成")
        time.sleep(5)
    return "success"

def add_job_scheduler(handler, job_id, job_cron, args):
    minute, hour, day, month, day_of_week = job_cron.split(",")
    if day_of_week != "*":
        day_of_week = str(int(day_of_week) - 1)
    _job_args = {
        'func': schedule_check,
        'id': str(job_id),
        'args': args,
        'trigger': {
            'type': 'cron',
            'day_of_week': day_of_week,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute
        }
    }
    print(_job_args)
    handler.add_job(**_job_args)


def test_job(job_id):
    import datetime
    print(datetime.datetime.now() ," Job is Running: ", job_id)


if __name__ == '__main__':
    auto_check('zj','NEWSAP2')