from pydantic import BaseModel, ConfigDict, field_validator, with_config


# this config allows to raise error on extra properties and allow to create objects from attributes
@with_config(ConfigDict(extra="forbid", from_attributes=True))
class NewQuote(BaseModel):
    """New quote payload validator."""

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
