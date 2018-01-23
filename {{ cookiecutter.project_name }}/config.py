
class Config:
    SECRET_KEY = 'my secret key'
    TEMPLATES_AUTO_RELOAD = False


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    pass


config = {
    'default': DevelopmentConfig,
    'production': ProductionConfig,
}
