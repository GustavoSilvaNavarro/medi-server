# ruff: noqa: RUF012
from sqladmin import ModelView

from app.db.models.quotes import Quotes


class QuotesAdmin(ModelView, model=Quotes):
    """Integration admin with quotes table."""

    name_plural = "Quotes"
    page_size = 100
    page_size_options = [25, 50, 100, 200]
    column_searchable_list = [Quotes.id, Quotes.quote]
    column_list = [Quotes.id, Quotes.quote, Quotes.created_at, Quotes.updated_at, Quotes.deleted_at]
