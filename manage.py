from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from webapp import app
from exts import db
from models import User, Host, History, Jobs

# init 初始化，第一次使用
# python manage.py db init
# 模型更改需要再次迁移
# migrate
# python manage.py db migrate
# upgrade
# python manage.py db upgrade
# 模型 -> 迁移文件 -> 表

manager = Manager(app)
# 要使用flask_migrate,必须绑定app和db
migrate = Migrate(app, db)
# 把MigrateCommand 命令添加到manager中
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()