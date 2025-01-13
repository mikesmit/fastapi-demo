from typing import Annotated
from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, StaticPool, create_engine
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from pathlib import Path
from app.settings import Environment, get_settings

# Generally following the guidance for SQL in fastAPI here
# https://fastapi.tiangolo.com/tutorial/sql-databases/

# NOTE: if you don't use StaticPool with in-memory sqlite you will get
# errors.
# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#configure-the-in-memory-database

def build_desktop_engine()->Engine:
    Path(".desktop").mkdir(parents=True, exist_ok=True)
    sqlite_url = f"sqlite:///.desktop/database.sqlite.db"
    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, connect_args=connect_args, poolclass=StaticPool)

def build_engine()->Engine:
    match get_settings().environment:
        case Environment.DESKTOP:
            return build_desktop_engine()

engine = build_engine()

SQLAlchemyInstrumentor().instrument(engine=engine, enable_commenter=True, commenter_options={})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]