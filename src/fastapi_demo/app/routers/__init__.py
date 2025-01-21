from fastapi import FastAPI

from fastapi_demo.core.auth.jwt_decoder import JWTDecoder
from .household import create_router as create_household_router
from .user import create_router as create_user_router
from fastapi_demo.core.database import SessionGeneratorFactory

def include_all_routers(app:FastAPI,
                        session_depedency:SessionGeneratorFactory,
                        optional_auth:JWTDecoder,
                        auth:JWTDecoder):
    app.include_router(create_household_router(session_dependency=session_depedency))
    app.include_router(create_user_router(session_dependency=session_depedency, 
                                          optional_auth=optional_auth,
                                          auth=auth))