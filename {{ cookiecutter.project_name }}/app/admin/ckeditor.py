"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-06-09 19:49:32
:last modified by:   stefan
:last modified time: 2019-06-09 19:50:42

"""
from wtforms.fields import TextAreaField
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    """CkEditor widget."""

    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " ckeditor"
        else:
            kwargs.setdefault("class", "ckeditor")
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    """CKEditor field."""

    widget = CKTextAreaWidget()


class CKEditorMixin:
    """Add CKEditor support."""
    edit_template = "admin/edit_ck.html"
    create_template = "admin/edit_ck.html"
