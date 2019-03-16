#!-*- coding: utf-8 -*-
"""
:author: Stefan Lehmann <stefan.st.lehmann@gmail.com>

"""
from wtforms import form, fields, validators
from wtforms.validators import required
from ..models import User


MSG_REQUIRED = 'Dieses Feld ist erforderlich.'
MSG_LENGTH = 'Bitte verwenden Sie 1 bis 64 Zeichen.'
MSG_EMAIL = 'Bitte geben Sie eine gültige Email-Adresse ein.'


class LoginForm(form.Form):
    username = fields.TextField(
        'Benutzername:', validators=[required(MSG_REQUIRED)])

    password = fields.PasswordField(
        'Passwort:', validators=[required(MSG_REQUIRED)])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Ungültiger Benutzername')

        if not user.verify_password(self.password.data):
            raise validators.ValidationError('Ungültiges Passwort')

    def get_user(self):
        return User.query.filter_by(username=self.username.data).first()
