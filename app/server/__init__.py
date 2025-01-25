from fastapi import FastAPI

from app.adapters import logger
from app.config import config

# from .admin import start_admin
from .routes import router


def start_server(server: FastAPI) -> FastAPI:
    """Run server and attach all the endpoints.

    Returns:
        FastAPI: The FastAPI server instance with routes attached.

    """
    server.include_router(router=router, prefix=f"/{config.URL_PREFIX}" if config.URL_PREFIX else "")
    # start_admin(server=server)

    logger.info("Server is starting...")
    return server
