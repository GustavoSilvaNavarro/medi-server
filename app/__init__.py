from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.server import start_server
from app.server.errors import CustomError

from .adapters import init_loggers, logger
from .config import config
from .db import connections

app = FastAPI()


@app.exception_handler(CustomError)
def custom_error(_req: Request, err: CustomError) -> JSONResponse:
    """Handle custom errors and return a JSON response.

    Returns:
        JSONResponse: A JSON response with the error details and status code.
    """
    logger.error(err)
    return JSONResponse(status_code=err.status_code, content=jsonable_encoder(err.serialize_error()))


@app.exception_handler(Exception)
def global_error(_req: Request, err: Exception) -> JSONResponse:
    """Global Error handler.

    Returns:
       JSONResponse: A JSON response with a 500 status code and error details.
    """
    logger.error(err)
    return JSONResponse(status_code=500, content={"error": "Server Error", "detail": str(err) or None})


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
    await connections.engine.dispose()


app.add_event_handler("startup", start_app)
app.add_event_handler("shutdown", shutdown_app)
