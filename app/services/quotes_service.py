from fastapi import Request
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import Quotes
from app.schemas import NewQuote, NewQuoteResponse, NewQuotes
from app.server.errors import BadRequestError

REDIS_TOTAL_QUOTES_COUNT_PREFIX = "total-quotes-count"


async def stores_new_quote(req: Request, payload: NewQuote, db: AsyncSession) -> NewQuoteResponse:
    """Store a new single quote in the db.

    Returns:
        Quotes: The newly created quote object.
    """
    cache_total_count = await total_number_of_quotes(req=req, db=db)
    new_quote = Quotes(**payload.model_dump())
    db.add(new_quote)
    await db.commit()

    await req.app.state.redis.set_val(key=REDIS_TOTAL_QUOTES_COUNT_PREFIX, value=cache_total_count + 1)
    return NewQuoteResponse.model_validate(new_quote)


async def get_all_quotes(db: AsyncSession) -> list[NewQuoteResponse]:
    """Retrieve all quotes from the database.

    Args:
        db (AsyncSession): The database session to use for the query.

    Returns:
        list[NewQuoteResponse]: A list of all quotes in the database.
    """
    quotes_records = await db.execute(select(Quotes))
    quotes = quotes_records.scalars().all()

    return [NewQuoteResponse.model_validate(quote) for quote in quotes]


async def retrieve_single_quote(quote_id: int, db: AsyncSession) -> NewQuoteResponse:
    """Retrieve a single quote by its ID from the database.

    Args:
        quote_id (int): The ID of the quote to retrieve.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse: The quote object if found.

    Raises:
        BadRequestError: If quote with given ID doesn't exist.
    """
    quote = await db.scalar(select(Quotes).filter_by(id=quote_id))

    if not quote:
        msg = f"Quote does not exist for ID: {quote_id}"
        raise BadRequestError(msg)
    return NewQuoteResponse.model_validate(quote)


async def total_number_of_quotes(req: Request, db: AsyncSession) -> int:
    """Return the total count of quotes in the database.

    Returns:
        int: The total number of quotes.
    """
    cache_total_count = await req.app.state.redis.get_val(REDIS_TOTAL_QUOTES_COUNT_PREFIX)
    if cache_total_count:
        return int(cache_total_count)

    records = await db.execute(select(func.count()).select_from(Quotes))  # pylint: disable=not-callable
    total_count = records.scalar_one_or_none() or 0
    await req.app.state.redis.set_val(key=REDIS_TOTAL_QUOTES_COUNT_PREFIX, value=total_count)
    return total_count


async def stores_new_incoming_quotes(
    req: Request,
    payload: NewQuotes,
    db: AsyncSession,
) -> NewQuoteResponse | list[NewQuoteResponse]:
    """Store one or multiple new quotes in the database.

    Args:
        req (Request): The FastAPI request object.
        payload (NewQuotes): The quote(s) to be stored.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse | list[NewQuoteResponse]: Single quote response or list of quote responses.
    """
    if isinstance(payload.quotes, str):
        return await stores_new_quote(req=req, payload=NewQuote(quote=payload.quotes), db=db)

    new_quotes = [Quotes(quote=quote) for quote in payload.quotes]
    db.add_all(new_quotes)
    await db.commit()

    return [NewQuoteResponse.model_validate(quote for quote in new_quotes)]
