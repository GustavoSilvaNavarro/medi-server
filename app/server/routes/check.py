# ruff: noqa: ERA001
from typing import Any

from fastapi import APIRouter, Request, status

# from app.connections import connections

router = APIRouter()


@router.get(
    "/test",
    tags=["Test"],
    status_code=status.HTTP_200_OK,
)
async def yo_test_redis(req: Request) -> dict[str, str]:
    """Check the condition of the server to ensure it is running.

    Returns:
        Response: A response with status code 204 indicating the server is healthy.
    """
    # await connections.rc.set_value("test", {"msg": "GSN"})
    await req.app.state.redis.set_value("test", {"msg": "GSN"})
    return {"msg": "success"}


@router.get(
    "/result",
    tags=["Test"],
    status_code=status.HTTP_200_OK,
)
async def result_test_redis(req: Request) -> dict[str, Any]:
    """Check the condition of the server to ensure it is running.

    Returns:
        Response: A response with status code 204 indicating the server is healthy.
    """
    # res = await connections.rc.get_value("test", dict[str, str])
    res = await req.app.state.redis.get_value("test", dict[str, str])
    return {"msg": res}
