from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Quotes
from app.schemas import NewQuote, NewQuoteResponse


async def stores_new_quote(payload: NewQuote, db: AsyncSession) -> NewQuoteResponse:
    """Store a new single quote in the db.

    Returns:
        Quotes: The newly created quote object.
    """
    new_quote = Quotes(**payload.model_dump())
    db.add(new_quote)
    await db.commit()

    return NewQuoteResponse.model_validate(new_quote)
