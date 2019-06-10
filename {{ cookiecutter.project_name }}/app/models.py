"""Database models.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-12 18:08:55
:last modified by:   stefan
:last modified time: 2019-06-09 19:39:34

"""
import os
from . import db, login_manager, images, files
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.event import listens_for
from .orderable import OrderableModelMixin


class FileMixin(db.Model):
    """Mixin for file handling."""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=True, nullable=False)
    _upload_set = None

    def __repr__(self):
        return self.filename

    @property
    def url(self):
        return self._upload_set.url(self.filename)

    @property
    def filepath(self):
        return self._upload_set.path(self.filename)


class Image(FileMixin, db.Model):
    """Image model."""

    __tablename__ = "images"
    _upload_set = images


@listens_for(Image, "after_delete")
def delete_image(mapper, connection, target):
    if target.filepath:
        # Delete image
        try:
            os.remove(target.filepath)
        except OSError:
            pass


class File(FileMixin, db.Model):
    """File model."""

    __tablename__ = "files"
    _upload_set = files


@listens_for(File, "after_delete")
def delete_file(mapper, connection, target):
    if target.filepath:
        # Delete image
        try:
            os.remove(target.filepath)
        except OSError:
            pass


class Permission:
    """Permissions for the users."""
    MODIFY = 0x01
    ADMINISTER = 0x80


class Role(db.Model):
    """User roles."""
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __repr__(self):
        return f"<Role \"{self.name}\">"

    def __str__(self):
        return self.name


class StaticPage(OrderableModelMixin, db.Model):

    __tablename__ = "static_pages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    text = db.Column(db.Text())

    def __str__(self):
        return self.name


class User(UserMixin, db.Model):
    """User object."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True)
    email = db.Column(db.String(254), unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", backref="users")

    def __repr__(self):
        return "<User %r>" % self.username

    def __str__(self):
        return self.username

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permissions: Permission):
        """Return True if the user has the given permission."""
        return (
            self.role is not None and
            (self.role.permissions & permissions) == permissions
        )

    def is_administrator(self):
        """Return True if the user is an administrator."""
        return self.can(Permission.ADMINISTER)


@login_manager.user_loader
def load_user(user_id):
    """User loader."""
    return User.query.get(user_id)
