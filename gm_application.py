from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_moment import Moment
from flask_redis import FlaskRedis
from simpleMqAdaptor import SimpleMqAdaptor
from config import config

bootstrap = Bootstrap()
mongo = PyMongo()
login_manager = LoginManager()
babel = Babel()
moment = Moment()
mysql_db = SQLAlchemy()
redis_store = FlaskRedis()
mqAdaptor = SimpleMqAdaptor('localhost')


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    bootstrap.init_app(app)
    mongo.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)
    moment.init_app(app)
    mysql_db.init_app(app)
    redis_store.init_app(app)

    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'

    if not app.debug:
        import logging
        from logging.handlers import TimedRotatingFileHandler
        warn_file_handler = TimedRotatingFileHandler(filename="gm_tools.info.log", when='midnight', interval=1,
                                                     encoding="utf8")
        warn_file_handler.setLevel(logging.INFO)
        app.logger.addHandler(warn_file_handler)

        error_file_handler = TimedRotatingFileHandler(filename="gm_tools.error.log", when='midnight', interval=1,
                                                      encoding="utf8")
        error_file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_file_handler)

    return app
