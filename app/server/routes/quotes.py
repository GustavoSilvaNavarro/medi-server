from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections import connections
from app.schemas import NewQuote, NewQuoteResponse, NewQuotes
from app.services import (
    get_all_quotes,
    process_and_store_audio_quote,
    retrieve_single_quote,
    stores_new_bulk_incoming_quotes,
    stores_new_quote,
    total_number_of_quotes,
    update_quote_record,
)

router = APIRouter()


@router.post(
    "/meditation/audio",
    description="Receives audio, process it and stores the text in db.",
    status_code=status.HTTP_201_CREATED,
)
async def upload_audio(
    req: Request,
    audio_file: Annotated[UploadFile, File(description="Meditation quote audio")],
    db: Annotated[AsyncSession, Depends(connections.get_db)],
) -> NewQuoteResponse:
    """Create a new quote in the database by processing audio.

    Args:
        req (Request): The FastAPI request object.
        audio_file (UploadFile): Audio quote to process and store.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse: The created quote object.
    """
    return await process_and_store_audio_quote(req=req, audio_file=audio_file, db=db)


@router.post(
    "/new-quote",
    description="Creates new quote",
    status_code=status.HTTP_201_CREATED,
)
async def add_new_single_quote(
    req: Request,
    payload: NewQuote,
    db: Annotated[AsyncSession, Depends(connections.get_db)],
) -> NewQuoteResponse:
    """Create a new quote in the database.

    Args:
        req (Request): The FastAPI request object.
        payload (NewQuote): The data for the new quote.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse: The created quote object.
    """
    return await stores_new_quote(req=req, payload=payload, db=db)


@router.post(
    "/add/quotes",
    description="Add new quotes in the db as bulk",
    status_code=status.HTTP_201_CREATED,
)
async def insert_quotes_in_bulk(
    req: Request,
    payload: NewQuotes,
    db: Annotated[AsyncSession, Depends(connections.get_db)],
) -> NewQuoteResponse | list[NewQuoteResponse]:
    """Store either a new single or list of quotes.

    Args:
        req (Request): The FastAPI request object.
        payload (NewQuotes): Payload single or list of quotes.
        db (AsyncSession): The database session.

    Returns:
        list[NewQuoteResponse | list[NewQuoteResponse]: A list of all quotes in the database.
    """
    return await stores_new_bulk_incoming_quotes(req=req, payload=payload, db=db)


@router.get(
    "/",
    description="Retrieves list of all quotes in db.",
    status_code=status.HTTP_200_OK,
)
async def get_list_all_quotes(db: Annotated[AsyncSession, Depends(connections.get_db)]) -> list[NewQuoteResponse]:
    """Retrieve a list of all quotes from the database.

    Args:
        db (AsyncSession): The database session to use for the query.

    Returns:
        list[NewQuoteResponse]: A list of all quotes in the database.
    """
    return await get_all_quotes(db=db)


@router.get(
    "/quote/{quote_id}",
    description="Retrieves a single quote based on ID",
    status_code=status.HTTP_200_OK,
)
async def get_single_quote(quote_id: int, db: Annotated[AsyncSession, Depends(connections.get_db)]) -> NewQuoteResponse:
    """Retrieve a single quote by its ID.

    Args:
        quote_id (int): The ID of the quote to retrieve.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse: The requested quote.
    """
    return await retrieve_single_quote(quote_id=quote_id, db=db)


@router.get(
    "/get-total-quotes",
    description="Returns the total count of records in the quotes table.",
    status_code=status.HTTP_200_OK,
)
async def get_total_of_quotes(
    req: Request,
    db: Annotated[AsyncSession, Depends(connections.get_db)],
) -> dict[str, str | int]:
    """Get the total number of quotes in the database.

    Args:
        req (Request): The FastAPI request object.
        db (AsyncSession): The database session.

    Returns:
        dict[str, str | int]: Dictionary containing status and total count.
    """
    total_rows = await total_number_of_quotes(req=req, db=db)
    return {"status": "success", "total_count": total_rows}


@router.put("/update/{quote_id}", description="Updates quote record", status_code=status.HTTP_200_OK)
async def update_quote(
    quote_id: int,
    payload: NewQuote,
    db: Annotated[AsyncSession, Depends(connections.get_db)],
) -> NewQuoteResponse:
    """Return an updated quote record.

    Args:
        quote_id (int): The ID of the quote to be updated.
        payload (NewQuote): Data to update quote.
        db (AsyncSession): The database session.

    Returns:
        NewQuoteResponse: The requested quote.
    """
    return await update_quote_record(quote_id=quote_id, payload=payload, db=db)
