from fastapi import Request, UploadFile
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.adapters.elevenlabs import el
from app.config import config
from app.db.models import Quotes
from app.helpers import audio_length_under_limit
from app.schemas import NewQuote, NewQuoteResponse, NewQuotes
from app.server.errors import BadRequestError


async def process_and_store_audio_quote(
    req: Request,
    audio_file: UploadFile | None,
    db: AsyncSession,
) -> NewQuoteResponse:
    """Process and stores new quote in the database by processing audio.

    Args:
        req (Request): The FastAPI request object.
        audio_file (UploadFile): Audio quote to process and store.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse: The created quote object.

    Raises:
        BadRequestError: If the audio exceeds the length limit.
    """
    audio_bytes = await audio_file.read()
    if not audio_length_under_limit(audio=audio_bytes):
        msg = "Audio with new quote exceed length limit"
        raise BadRequestError(msg)

    quote = el.convert_speech_to_text(audio=audio_bytes)
    new_quote = Quotes(quote=quote)
    db.add(new_quote)
    await db.commit()

    await req.app.state.redis.set_val(
        key=config.TOTAL_QUOTES_COUNT_PREFIX,
        value=new_quote.id,
        expire=config.CACHE_EXPIRATION_IN_SECONDS,
    )
    return new_quote


async def stores_new_quote(req: Request, payload: NewQuote, db: AsyncSession) -> NewQuoteResponse:
    """Store a new single quote in the db.

    Returns:
        Quotes: The newly created quote object.
    """
    new_quote = Quotes(**payload.model_dump())
    db.add(new_quote)
    await db.commit()

    await req.app.state.redis.set_val(
        key=config.TOTAL_QUOTES_COUNT_PREFIX,
        value=new_quote.id,
        expire=config.CACHE_EXPIRATION_IN_SECONDS,
    )
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
    cache_total_count = await req.app.state.redis.get_val(config.TOTAL_QUOTES_COUNT_PREFIX)
    if cache_total_count:
        return int(cache_total_count)

    records = await db.execute(select(func.count()).select_from(Quotes))  # pylint: disable=not-callable
    total_count = records.scalar_one_or_none() or 0
    await req.app.state.redis.set_val(
        key=config.TOTAL_QUOTES_COUNT_PREFIX,
        value=total_count,
        expire=config.CACHE_EXPIRATION_IN_SECONDS,
    )
    return total_count


async def stores_new_bulk_incoming_quotes(
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

    await req.app.state.redis.set_val(
        key=config.TOTAL_QUOTES_COUNT_PREFIX,
        value=new_quotes[-1].id,
        expire=config.CACHE_EXPIRATION_IN_SECONDS,
    )
    return new_quotes


async def update_quote_record(quote_id: int, payload: NewQuote, db: AsyncSession) -> NewQuoteResponse:
    """Update a quote record in a database.

    Args:
        quote_id (int): unique identifier of the quote record.
        payload (NewQuote): data that will be used to update a quote record.
        db (AsyncSession): DB session.

    Returns:
        NewQuoteResponse: Updated quote.

    Raises:
        BadRequestError: If quote with given ID doesn't exist.
    """
    quote = await db.scalar(select(Quotes).filter_by(id=quote_id))
    if not quote:
        msg = f"Quote with ID {quote_id} does not exist."
        raise BadRequestError(msg)

    updated_quote = payload.model_dump(exclude_unset=True)
    for key, value in updated_quote.items():
        setattr(quote, key, value)  # Dynamically set attribute on the SQLAlchemy ORM object

    await db.commit()
    await db.refresh(quote)
    return quote
    return quote
    return quote
    return quote
