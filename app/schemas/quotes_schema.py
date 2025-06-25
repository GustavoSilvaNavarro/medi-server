# pylint: disable=missing-class-docstring
from datetime import datetime

from pydantic import BaseModel, field_validator


# this config allows to raise error on extra properties and allow to create objects from attributes
class NewQuote(BaseModel):
    """New quote payload validator."""

    model_config = {"extra": "forbid", "from_attributes": True}

    quote: str

    @field_validator("quote")
    @classmethod
    def check_non_empty_value(cls, value: str) -> str:
        """Validate that the provided value is not empty or whitespace.

        Args:
            value (str): The value to validate.

        Returns:
            str: The validated value if it is not empty or whitespace.

        Raises:
            ValueError: If the value is empty or consists only of whitespace.
        """
        if not value or not value.strip():
            msg = f"Value: {value}, can not be empty."
            raise ValueError(msg)
        return value


class NewQuoteResponse(BaseModel):
    """Output for newly created quote."""

    model_config = {"from_attributes": True}

    id: int
    quote: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class NewQuotes(BaseModel):
    """New quotes payload validator."""

    model_config = {"extra": "forbid", "from_attributes": True}

    quotes: str | list[str]

    @field_validator("quotes")
    @classmethod
    def check_non_empty_value(cls, value: str | list[str]) -> str | list[str]:
        """Validate that the provided value is not empty.

        Args:
            value (str | list[str]): The value to validate, either a string or list of strings.

        Returns:
            str | list[str]: The validated value.

        Raises:
            ValueError: If the value is empty or consists only of whitespace,
                       or if it's a list containing empty strings.
        """
        if isinstance(value, str):
            if not value or not value.strip():
                msg = f"Value: {value}, can not be empty."
                raise ValueError(msg)
            return value

        if not value:  # Empty list check
            msg = f"Quote list cannot be empty => Value: {value}"
            raise ValueError(msg)

        for quote in value:
            if not quote or not quote.strip():
                msg = "Quote strings in list cannot be empty."
                raise ValueError(msg)
        return value
