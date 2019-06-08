"""Database models.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-12 18:08:55
:last modified by:   stefan
:last modified time: 2019-06-02 19:54:37

"""
from . import db, login_manager, images
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Image(db.Model):
    """Image model."""

    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=True)

    def __repr__(self):
        return self.filename

    @property
    def url(self):
        return images.url(self.filename)

    @property
    def filepath(self):
        return images.path(self.filename)


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
