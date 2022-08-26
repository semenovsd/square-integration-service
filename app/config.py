import os
import secrets
from typing import List, Union

from pydantic import (AnyHttpUrl, BaseSettings, validator)


class BaseAppSettings(BaseSettings):

    class Config:
        case_sensitive = True
        env_file = '../.env' if os.environ.get('ENV_STAGE') is None else None  # Export env vars for local deployment


class Settings(BaseAppSettings):
    ENV_STAGE: str
    DEBUG: bool = False
    PROJECT_NAME: str = 'Square Integration Service'
    PROJECT_VERSION: str = '1.0'
    PROJECT_DESCRIPTION: str = 'Square Integration Service'
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
