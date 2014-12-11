import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    TALKS_PER_PAGE = 7
    COMMENTS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 10
    #being imported in the __init__ file:
    # ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
    # email server
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'raufguy@gmail.com'
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PASSWORD = 'pass'

    SQLALCHEMY_RECORD_QUERIES = True
    # slow database query threshold (in seconds)
    DATABASE_QUERY_TIMEOUT = 0.5

    # administrator list
    ADMINS = ['raufguy@gmail.com']

    def __init__(self):
        pass

class DevelopmentConfig(Config):

    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'raufguy@gmail.com'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    WHOOSH_BASE = os.path.join(basedir, 'search.db')
    #SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    def __init__(self):
        Config.__init__(self)

class TestingConfig(Config):

    TESTING = True
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    #SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    def __init__(self):
        Config.__init__(self)

class ProductionConfig(Config):


    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    #SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    def __init__(self):
        Config.__init__(self)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# administrator list
ADMINS = ['raufguy@gmail.com']


# -*- coding: utf-8 -*-
# ...
# available languages
LANGUAGES = {
    'en': 'English',
}
