from typing import Any, Callable
from fastapi import FastAPI
from sqlalchemy import Engine

from fastapi_demo.core.auth.jwt_decoder import JWTDecoder
from fastapi_demo.core.database import create_session_dep
from .routers import include_all_routers

'''
Application defined as routers completely indipendent of environment allowing it
to easily be run in whatever cloud provider container or desktop or test environment.
'''

def initialize(app:FastAPI,
               engine:Engine,
               jwt_issuer:str,
               jwt_audience:str):
    '''
    attach all routes to the app and configure them to use the provided SQLModel engine
    and jwt settings.
    '''
    optional_auth = JWTDecoder(jwt_issuer, 
                    audience=jwt_audience,
                    auto_error=False)
    auth = JWTDecoder(jwt_issuer, 
                    audience=jwt_audience,
                    auto_error=True)
    include_all_routers(app,
                        session_depedency=create_session_dep(engine),
                        optional_auth=optional_auth,
                        auth=auth)