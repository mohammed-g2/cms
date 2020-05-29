import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lere5eev.w57w68'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SLOW_DB_QUERY_TIME = 0.5
    
    POSTS_PER_PAGE = 5
    FOLLOWERS_PER_PAGE = 10
    MAIL_SUBJECT_PREFIX = '[Blog]'

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '25')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER') or 'BLOG [admin@email.com]'
    ADMIN = os.environ.get('ADMIN') or 'admin@email.com'
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'


class ProductionsConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionsConfig,
    'default': DevelopmentConfig
}