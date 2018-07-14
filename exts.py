import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    return app


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


if __name__ == '__main__':
    auto_check('zj','NEWSAP2')