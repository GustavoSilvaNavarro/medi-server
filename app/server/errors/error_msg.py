from typing import Optional

from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """Basic error message object."""

    message: str
    field: Optional[str] = None
