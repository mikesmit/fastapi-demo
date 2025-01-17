from enum import Enum
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(Enum):
    DESKTOP = "desktop"
    PRODUCTION = "production"
    
class AppSettings(BaseSettings):
    environment:Environment = Environment.DESKTOP

    jwt_issuer:str = "https://your_issuer/"
    '''
    The issuer that must sign any JWT bearer token before the API with accept it as valid
    '''
    jwt_audience:str = "https://your_api/"
    '''
    The audience that any JWT bearer token must include in order to be accepted by the API
    '''
    
    model_config = SettingsConfigDict(env_file=".env")
    pass


@lru_cache
def get_settings():
    return AppSettings()