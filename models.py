from web_init import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=0)
    status = db.Column(db.SmallInteger, default=0)

# id, type, cluster, hostname
class Host(db.Model):
    __tablename__ = 'host'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(32), index=True, nullable=False)
    cluster = db.Column(db.String(32), index=True, nullable=False)
    hostname = db.Column(db.String(32), unique=True, nullable=False)


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    checktime = db.Column(db.String(64), nullable=False)
    hostname = db.Column(db.String(32), nullable=False)
    type = db.Column(db.String(32), nullable=False)


class Jobs(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    content = db.Column(db.String(64), nullable=False)
    cron_time = db.Column(db.String(64), nullable=False)
    status = db.Column(db.SmallInteger, default=0)