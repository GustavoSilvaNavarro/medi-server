from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.connections import connections
from app.schemas import NewQuote, NewQuoteResponse
from app.services import stores_new_quote

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
