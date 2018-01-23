from flask import Flask
from .main import main
from config import config


def create_app(config_name: str='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.register_blueprint(main)

    return app
