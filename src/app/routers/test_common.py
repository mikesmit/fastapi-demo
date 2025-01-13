from fastapi import APIRouter, FastAPI
from sqlmodel import SQLModel

from app.database import create_db_and_tables, engine


def createApi(router:APIRouter):
    api = FastAPI()
    SQLModel.metadata.drop_all(bind=engine)
    api.include_router(router)
    create_db_and_tables()
    return api