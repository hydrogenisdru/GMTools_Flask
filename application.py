from flask import Flask
from config import config
from flask import Blueprint
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_moment import Moment
from flask_redis import FlaskRedis
from simpleMqAdaptor import SimpleMqAdaptor
from proto.Server2ServerProtocolProvider import Server2ServerProtocolProvider

# from flask_apscheduler import APScheduler

bootstrap = Bootstrap()
mongo = PyMongo()
mongo_analysis = PyMongo()
login_manager = LoginManager()
babel = Babel()
moment = Moment()
mysql_db = SQLAlchemy()
redis_store = FlaskRedis()
mqAdaptor = SimpleMqAdaptor('localhost')
proto = Server2ServerProtocolProvider()
# scheduler = APScheduler()
bluePrint = Blueprint('blue_print', __name__, static_folder='static', template_folder='templates')


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
    # scheduler.init_app(app)
    mongo_analysis.init_app(app, config_prefix='MONGO2')
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'login'

    if not app.debug:
        import logging
        from logging.handlers import TimedRotatingFileHandler
        warn_file_handler = TimedRotatingFileHandler(filename="./log/gm_tools.info.log", when='midnight', interval=1,
                                                     encoding="utf8")
        warn_file_handler.setLevel(logging.INFO)
        app.logger.addHandler(warn_file_handler)

        error_file_handler = TimedRotatingFileHandler(filename="./log/gm_tools.error.log", when='midnight', interval=1,
                                                      encoding="utf8")
        error_file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_file_handler)

    return app
