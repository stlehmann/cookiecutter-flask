import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from .main import main
from .config import config


db = SQLAlchemy()
migrate = Migrate()
toolbar = DebugToolbarExtension()
admin = Admin(name="{{ cookiecutter.project_name }}", template_mode="bootstrap3")


def create_app(config_name: str = os.environ.get("FLASK_ENV", "production")):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    toolbar.init_app(app)

    app.register_blueprint(main)

    return app
