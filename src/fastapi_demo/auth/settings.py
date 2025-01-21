from functools import lru_cache
from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict

#see https://fastapi.tiangolo.com/advanced/settings


class AuthSettings(BaseSettings):
    jwt_issuer:str = "https://your_issuer/"
    '''
    The issuer that must sign any JWT bearer token before the API with accept it as valid
    '''
    jwt_audience:str = "https://your_api/"
    '''
    The audience that any JWT bearer token must include in order to be accepted by the API
    '''
    
    model_config = SettingsConfigDict(env_file=".auth.env")

@lru_cache
def get_auth_settings():
    return AuthSettings()
