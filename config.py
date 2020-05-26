import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lere5eev.w57w68'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SUBJECT_PREFIX = '[Blog]'
    ADMIN = os.environ.get('ADMIN') or 'admin@email.com'
    POSTS_PER_PAGE = 5
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    MAIL_SERVER = os.environ.get('DEV_MAIL_SERVER') or 'localhost'
    MAIL_PORT = int(os.environ.get('DEV_MAIL_PORT') or '25')
    MAIL_USE_TLS = os.environ.get('DEV_MAIL_USE_TLS', '0').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('DEV_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('DEV_MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('DEV_MAIL_SENDER') or 'Blog <example@email.com>'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'


class ProductionsConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '25')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')
    ADMIN = os.environ.get('ADMIN')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionsConfig,
    'default': DevelopmentConfig
}