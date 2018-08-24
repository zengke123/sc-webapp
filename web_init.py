import os
import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
db = SQLAlchemy()
scheduler = APScheduler()
def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    scheduler.init_app(app)
    return app

# scheduler = APScheduler()
# app = create_app()
# scheduler.init_app(app)
