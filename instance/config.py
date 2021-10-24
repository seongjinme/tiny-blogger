from os import path, urandom

basedir = path.abspath(path.dirname(__file__))


class Config:
    SECRET_KEY = urandom(24)
    TESTING = False


class ProductionConfig(Config):
    DATABASE = path.join(basedir, 'blog.sqlite')


class DevelopmentConfig(Config):
    SECRET_KEY = 'tiny-blogger-in-dev'
    DATABASE = path.join(basedir, 'dev.sqlite')


class TestingConfig(Config):
    DATABASE = path.join(basedir, 'testing.sqlite')
    TESTING = True
