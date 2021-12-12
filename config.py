import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "shhhh... its private."
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SUBJECT_PREFIX = "[My Application]"
    MAIL_SENDER = "My Application <no-reply@gmail.com>"

    @staticmethod
    def init_app(app):
        # Config specific initialization can be performed.
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_ADMIN = os.environ.get("MAIL_ADMIN")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
                              "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")

    LOCAL_MOMENT = "js/lib/moment-with-locales.min.js"
    # serve bootstrap resources from local.
    BOOTSTRAP_SERVE_LOCAL = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TESTING_DATABASE_URL") or \
                              "sqlite:///" + os.path.join(basedir, "data-test.sqlite")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
                              "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
