from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI

from fastapi_demo.core.database import create_sqlite_engine


engine = create_sqlite_engine()

def createApi(router:APIRouter):
    api = FastAPI()
    api.include_router(router)
    return api