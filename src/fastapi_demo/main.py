from contextlib import asynccontextmanager
from fastapi import FastAPI
import fastapi_demo.routers as routers
import fastapi_demo.database as database
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from .opentelemetry import initialize
from .settings import get_settings

print(f"Initializing with settings F{get_settings().environment}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(routers.household_router)
app.include_router(routers.user_router)

initialize(app)

FastAPIInstrumentor.instrument_app(app)
