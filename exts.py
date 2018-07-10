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
    # RETN=0000, DESC=OK
    # RETN=0006
    if 'RETN=0000' in result:
        flag = True
    else:
        flag = False
    # print(child.before)
    child.sendline('quit')
    # print(child.before)
    child.close()
    return flag