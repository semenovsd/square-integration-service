from functools import partial

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from apis.rest_api.api_v1.routers import square_router
from config import settings
from interfaces.https.square.interface import SquareInterface

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)


async def startup(app: FastAPI) -> None:
    # Get setting configs
    app.state.settings = settings
    # Square Interface setup
    app.state.square_interface = SquareInterface()
    await app.state.square_interface.setup()


async def shutdown(app: FastAPI) -> None:
    await app.state.square_interface.shutdown()


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_event_handler(event_type="startup", func=partial(startup, app=app))
app.add_event_handler(event_type="shutdown", func=partial(shutdown, app=app))

app.include_router(square_router)
