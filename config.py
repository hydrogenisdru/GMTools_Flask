import os

from flask_bootstrap import WebCDN

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nothing'
    DEFAULT_USER = 'root'
    DEFAULT_PWD = '1234'
    DEFAULT_AUTH = 'admin'
    MQ_IP_ADDRESS = 'localhost'
    MONGO_URI = 'mongodb://123.59.71.187:27027/fire2'
    MONGO2_URI = 'mongodb://120.92.133.11:27077/analysis'
    REDIS_URL = 'redis://:@120.92.216.136:6770/0'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:1234@localhost:3306/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAGE_SIZE = 10
    MAIN_SERVER_CONFIG_FOLDER = '/Users/zouyang/Desktop/redis_data'
    DEPLOY_CONFIG_FOLDER = '/Users/zouyang/Desktop/redis_data'
    DEPLOY_SHELL_SCRIPT = 'config_update.sh'
    UPLOAD_FOLDER = '/Users/zouyang/Desktop/redis_data'
    UNZIP_FOLER_FIX = 'unzip_folder'
    BASE_CDN_FOLDER = '/ClientAssets'

    JOBS = [
        {
            'id': 'job1',
            'func': 'tasks:add',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 10
        }
    ]

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    SCHEDULER_API_ENABLED = True

    @staticmethod
    def init_app(app):
        app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
            '//cdn.bootcss.com/jquery/2.1.1/'
        )
        app.extensions['bootstrap']['cdns']['bootstrap'] = WebCDN(
            '//cdn.bootcss.com/bootstrap/3.3.7/'
        )
        app.config['MONGO_AUTO_START_REQUEST'] = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
