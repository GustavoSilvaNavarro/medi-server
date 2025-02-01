from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connections import connections
from app.schemas import NewQuote, NewQuoteResponse
from app.services import get_all_quotes, retrieve_single_quote, stores_new_quote, total_number_of_quotes

router = APIRouter()


@router.post(
    "/new-quote",
    tags=["Quotes"],
    description="Creates new quote",
    status_code=status.HTTP_201_CREATED,
)
async def add_new_single_quote(
    payload: NewQuote,
    db: Annotated[AsyncSession, Depends(connections.get_db)],
) -> NewQuoteResponse:
    """Create a new quote in the database.

    Args:
        payload (NewQuote): The data for the new quote.
        db (AsyncSession): The database session.

    Returns:
        Quotes: The created quote object.
    """
    return await stores_new_quote(payload=payload, db=db)


@router.get(
    "/",
    tags=["Quotes"],
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
    tags=["Quotes"],
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
    tags=["Quotes"],
    description="Returns the total count of records in the quotes table.",
    status_code=status.HTTP_200_OK,
)
async def get_total_of_quotes(db: Annotated[AsyncSession, Depends(connections.get_db)]) -> dict[str, str | int]:
    """Get the total number of quotes in the database.

    Args:
        db (AsyncSession): The database session.

    Returns:
        dict[str, str | int]: Dictionary containing status and total count.
    """
    total_rows = await total_number_of_quotes(db=db)
    return {"status": "success", "total_count": total_rows}
