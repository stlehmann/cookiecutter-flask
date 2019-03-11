"""Flask config module.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-11 19:39:50
:last modified by:   stefan
:last modified time: 2019-03-11 19:42:24

"""


class Config:
    """Base configuration settings for development and production."""
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = 'my secret key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = False


class DevelopmentConfig(Config):
    """Development configuration."""
    pass


class ProductionConfig(Config):
    """Production configuration."""
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
