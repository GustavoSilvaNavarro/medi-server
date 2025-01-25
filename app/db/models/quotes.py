from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base_table import BaseModel


class Quotes(BaseModel):
    """Quotes table."""

    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    quote: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
