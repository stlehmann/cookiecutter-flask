"""Flask config module.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-11 19:39:50
:last modified by:   stefan
:last modified time: 2019-06-02 15:16:00

"""
import os


APP_DIR = os.path.abspath(os.path.dirname(__file__))
FILE_DIR = os.path.join(APP_DIR, "static/files")
IMAGE_DIR = os.path.join(APP_DIR, "static/images")


class Config:
    """Base configuration settings for development and production."""
    SECRET_KEY = os.environ["FLASK_SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(APP_DIR, "db", "data.sqlite")
    UPLOADED_IMAGES_DEST = IMAGE_DIR
    UPLOADED_IMAGES_URL = "/static/images/"

    UPLOADED_FILES_DEST = FILE_DIR
    UPLOADED_FILES_URL = "/static/files/"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    """Production configuration."""
    TEMPLATES_AUTO_RELOAD = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
