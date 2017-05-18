import os

from flask_bootstrap import WebCDN

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nothing'
    DEFAULT_USER = 'root'
    DEFAULT_PWD = '1234'
    DEFAULT_AUTH = 'admin'

    @staticmethod
    def init_app(app):
        app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
            '//cdn.bootcss.com/jquery/1.11.3/'
        )
        app.extensions['bootstrap']['cdns']['bootstrap'] = WebCDN(
            '//cdn.bootcss.com/bootstrap/3.3.5/'
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
