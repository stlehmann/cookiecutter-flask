import os
from flask import Flask
from flask_assets import Environment, Bundle
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_uploads import (
    UploadSet,
    DEFAULTS,
    IMAGES,
    configure_uploads,
    patch_request_class,
)
from .main import main
from .config import config


db = SQLAlchemy()
migrate = Migrate()
assets = Environment()
toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.login_view = "admin.login"
images = UploadSet("images", IMAGES)
files = UploadSet("files", DEFAULTS)


from .admin.modelviews import (
    MyAdminIndexView,
    UserModelView,
    ImageModelView,
    FileModelView,
)  # noqa: E402

admin = Admin(
    name="flask_app", index_view=MyAdminIndexView(), template_mode="bootstrap3"
)


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
    configure_uploads(app, (images, files))

    # patch image size to 16MB
    patch_request_class(app, 16 * 1024 * 1024)

    # webassets
    assets.init_app(app)
    sass = Bundle("styles.sass", filters="libsass", output="styles.css")
    assets.register("sass", sass)

    # register blueprints
    app.register_blueprint(main)

    # Admin views
    from .models import User, Image, File

    admin.add_view(ImageModelView(Image, db.session, name="Bilder"))
    admin.add_view(FileModelView(File, db.session, name="Dateien"))
    admin.add_view(UserModelView(User, db.session, name="Benutzer"))

    return app
