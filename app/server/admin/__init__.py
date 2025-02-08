from fastapi import FastAPI
from sqladmin import Admin

from app.connections import connections

from .models import QuotesAdmin


def start_admin(server: FastAPI) -> None:
    """Start Admin to manage DB using an interface (UI)."""
    admin = Admin(app=server, engine=connections.engine, base_url="/admin", title="Server DB Admin")

    # ? Registering models
    admin.add_view(QuotesAdmin)
