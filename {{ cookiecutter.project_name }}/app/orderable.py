"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-06-09 19:12:51
:last modified by:   stefan
:last modified time: 2019-06-10 12:12:07

"""
from . import db
from flask import redirect, url_for
from flask_admin.actions import action

def default_order_index(context) -> int:
    """Return default order value.

    This is the max value or order plus one.
    """
    if context:
        current_table_name = context.current_column.table.name
        query = db.engine.execute(f"SELECT MAX(\"order_index\") + 1 FROM {current_table_name}")
        order_index = query.first()[0]
        if order_index is None:
            return 0
        else:
            return order_index
    else:
        return 0


class OrderableModelMixin:
    """Mixin for orderable database objects."""

    order_index = db.Column(db.Integer, index=True, default=default_order_index)

    def _get_model_class(self):
        for c in db.Model._decl_class_registry.values():
            if (
                hasattr(c, "__tablename__")
                and c.__tablename__ == self.__tablename__
            ):
                return c

    def move_up(self) -> None:
        """Move item up."""
        self._model = self._get_model_class()
        items = self._model.query.order_by(self._model.order_index).all()
        id_ = items.index(self)

        # if first item then do nothing
        if id_ == 0:
            return

        # get the item before which we swap position with
        item_before = items[id_ - 1]

        # swap order_index numbers with the item before
        x = self.order_index
        self.order_index = item_before.order_index
        item_before.order_index = x

        db.session.add(self)
        db.session.add(item_before)
        db.session.commit()

        # normalize order_index numbers for all items
        for i, item in enumerate(
            self._model.query.order_by(self._model.order_index)
        ):
            item.order_index = i
        db.session.commit()

    def move_down(self) -> None:
        """Move item down."""
        self._model = self._get_model_class()
        items = self._model.query.order_by(self._model.order_index).all()
        id_ = items.index(self)

        # if first item then do nothing
        if id_ == len(items) - 1:
            return

        # get the item before which we swap position with
        item_after = items[id_ + 1]

        # swap order_index numbers with the item before
        x = self.order_index
        self.order_index = item_after.order_index
        item_after.order_index = x

        db.session.add(self)
        db.session.add(item_after)
        db.session.commit()

        # normalize order_index numbers for all items
        for i, item in enumerate(
            self._model.query.order_by(self._model.order_index)
        ):
            item.order_index = i
        db.session.commit()


class OrderableModelViewMixin:
    column_default_sort = ("order_index", False)
    list_template = "admin/list_orderable_model.html"

    @action(
        "move_up",
        "Nach oben bewegen",
        "Sollen die ausgewählten Elemente nach oben verschoben werden?",
    )
    def action_move_up(self, ids):
        selected = self.model.query.filter(self.model.id.in_(ids)).order_by(
            self.model.order_index
        )
        for item in selected:
            item.move_up()
        return redirect(url_for(".index_view"))

    @action(
        "move_down",
        "Nach unten bewegen",
        "Sollen die ausgewählten Elemente nach unten verschoben werden?",
    )
    def action_move_down(self, ids):
        selected = self.model.query.filter(self.model.id.in_(ids)).order_by(
            self.model.order_index.desc()
        )
        for item in selected:
            item.move_down()
        return redirect(url_for(".index_view"))
