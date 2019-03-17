import os
from flask import Flask
from flask_assets import Environment, Bundle
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from .main import main
from .config import config


db = SQLAlchemy()
migrate = Migrate()
assets = Environment()
toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = "admin.login"


from .admin.modelviews import MyAdminIndexView, UserModelView  # noqa: E402
admin = Admin(
    name="{{ cookiecutter.project_name }}",
    index_view=MyAdminIndexView(),
    template_mode="bootstrap3")


def create_app(config_name: str = os.environ.get("FLASK_ENV", "production")):
    """Create Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # type: ignore

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)
    bootstrap.init_app(app)
    toolbar.init_app(app)
    login_manager.init_app(app)

    # webassets
    assets.init_app(app)
    sass = Bundle(
        "styles.sass", filters="sass", output="styles.css"
    )
    assets.register("sass", sass)

    # register blueprints
    app.register_blueprint(main)

    # Admin views
    from .models import User
    admin.add_view(UserModelView(User, db.session, name="Benutzer"))

    return app
