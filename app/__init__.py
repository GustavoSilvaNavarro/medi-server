from fastapi import FastAPI

from app.server import start_server

from .adapters import init_loggers, logger
from .config import config

# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import JSONResponse


# from app.server.errors import CustomError

# from .db import connections

app = FastAPI()


# @app.exception_handler(CustomError)
# async def custom_error(_req: Request, err: CustomError) -> JSONResponse:
#     """Custom Error middleware."""
#     logger.error(err)
#     return JSONResponse(status_code=err.status_code, content=jsonable_encoder(err.serialize_error()))


# @app.exception_handler(Exception)
# async def global_error(_req: Request, err: Exception) -> JSONResponse:
#     """Global Error handler."""
#     logger.error(err)
#     return JSONResponse(status_code=500, content={"error": "Server Error", "detail": str(err) if str(err) else None})


def start_app() -> FastAPI:
    """Start FastApi Server with all its connections.

    Returns:
        FastAPI: The FastAPI application instance.

    """
    init_loggers(config.LOG_LEVEL)

    api_sever = start_server(app)

    logger.info("%s Service is starting...", config.SERVICE_NAME)
    logger.info("%s Server running on PORT %s", config.SERVICE_NAME, config.PORT)
    return api_sever


async def shutdown_app() -> None:
    """Shutdown FastAPI Server and Connections."""
    logger.info("Shutdown -> Server shutting down")
    # await connections.engine.dispose()


app.add_event_handler("startup", start_app)
app.add_event_handler("shutdown", shutdown_app)
