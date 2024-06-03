import os

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse



from routes.response_synthesizer_route import (
    init_response_synthesizer_router,
    
)
from routes.lead_generator_route import init_lead_generator_router

import config as env_config


def init_api() -> FastAPI:
    """
    Initializes the FastAPI instance.  This will wire up all middleware and routers.
    """
    # This sets the version for the OpenAPI and logging.  Make sure that you build your container and
    # set the version so that this is properly set when running.
    version = os.environ.get("VERSION", "DEV-SNAPSHOT")
    app = FastAPI(title="response-synthesyzer", version=version)
    _init_middleware(app, version)
    _init_routes(app)
    _init_errors_handlers(app=app)


    return app


def _init_middleware(app: FastAPI, version: str):
    """
    This function will initialize all middleware layers.
    """
    # Setup the ACV Structured logger

    origins = [env_config.ALLOWED_HOSTS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _init_routes(app: FastAPI):
    """
    This function will initialize all endpoint routers.
    """
    app.include_router(init_response_synthesizer_router())
    app.include_router(init_lead_generator_router())


def _init_errors_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        errors = [error["msg"] for error in exc.errors()]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(dict(success=False, errors=errors)),
        )
