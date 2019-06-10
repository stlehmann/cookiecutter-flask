"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-15 18:17:57
:last modified by:   stefan
:last modified time: 2019-06-10 11:39:58

"""
import os
import flask_login as login
from flask import redirect, url_for, request, flash
from flask_admin import AdminIndexView, expose, helpers, form
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup
from wtforms.fields import PasswordField
from .forms import LoginForm
from .ckeditor import CKEditorMixin, CKTextAreaField
from ..orderable import OrderableModelViewMixin
from ..config import IMAGE_DIR, FILE_DIR
from .. import images, files


def _list_thumbnail(view, context, model, name):
    if not model.filename:
        return ""

    return Markup(
        '<img src="{model.url}" style="width: 150px;">'.format(model=model)
    )


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


class ImageModelView(SecureModelView):
    """ModelView for images."""

    edit_template = "/admin/edit_image.html"
    create_template = "/admin/edit_image.html"
    list_template = "/admin/list_file.html"

    column_list = ["image", "filename"]

    column_labels = {"image": "Bild", "filename": "Dateiname"}

    column_formatters = {"image": _list_thumbnail}

    form_extra_fields = {
        "image": form.ImageUploadField(
            "Bild", base_path=IMAGE_DIR, url_relative_path="images/"
        )
    }

    # form_rules = [rules.FieldSet(("filename",))]

    def on_model_change(self, form, model, is_created):

        if form.image.data is None:
            if request.form["filename"] != request.form["old_filename"]:
                os.rename(
                    images.path(request.form["old_filename"]),
                    images.path(request.form["filename"])
                )

        else:
            if form.filename.data != form.image.data.filename:
                os.rename(
                    images.path(form.image.data.filename),
                    images.path(form.filename.data)
                )


class FileModelView(SecureModelView):
    """ModelView for files."""

    edit_template = "/admin/edit_file.html"
    create_template = "/admin/edit_file.html"
    list_template = "/admin/list_file.html"

    form_extra_fields = {
        "file": form.FileUploadField(
            "Datei", base_path=FILE_DIR
        )
    }

    def on_model_change(self, form, model, is_created):

        if form.file.data is None:
            if request.form["filename"] != request.form["old_filename"]:
                os.rename(
                    files.path(request.form["old_filename"]),
                    files.path(request.form["filename"])
                )

        else:
            if form.filename.data != form.file.data.filename:
                os.rename(
                    files.path(form.file.data.filename),
                    files.path(form.filename.data)
                )


class StaticPageModelView(CKEditorMixin, OrderableModelViewMixin, SecureModelView):

    column_default_sort = ("order_index", False)
    column_list = ["name"]
    form_overrides = {"text": CKTextAreaField}
    list_template = "admin/list_staticpage.html"
    form_rules = [rules.FieldSet(["name", "text"])]
    column_labels = {
        "name": "Name",
        "text": "Text",
    }


class UserModelView(SuperuserModelView):
    """ModelView for user management."""
    column_list = ["username", "role", "email"]

    form_rules = [
        rules.FieldSet(("username", "role", "email", "password"))
    ]

    form_extra_fields = {
        "password": PasswordField("Password")
    }
