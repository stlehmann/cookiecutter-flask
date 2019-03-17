"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-15 18:17:57
:last modified by:   stefan
:last modified time: 2019-03-17 19:13:24

"""
import flask_login as login
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose, helpers
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import PasswordField
from .forms import LoginForm


class MyAdminIndexView(AdminIndexView):
    """Main view of the admin interface."""

    @expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(MyAdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            if user is not None and user.verify_password(form.password.data):
                login.login_user(user)
            else:
                flash("Invalid username or password.")

        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))


class SecureModelView(ModelView):
    """Mixin for all views that are only for valid users."""

    def is_accessible(self):
        return login.current_user.is_active and login.current_user.is_authenticated


class SuperuserModelView(ModelView):
    """Mixin that allows only super users access."""

    def is_accessible(self):
        return (
            login.current_user.is_active
            and login.current_user.is_authenticated
            and login.current_user._get_current_object().is_administrator()
        )


class UserModelView(SuperuserModelView):
    """ModelView for user management."""
    column_list = ["username", "role", "email"]

    form_rules = [
        rules.FieldSet(("username", "role", "email", "password"))
    ]

    form_extra_fields = {
        "password": PasswordField("Password")
    }
