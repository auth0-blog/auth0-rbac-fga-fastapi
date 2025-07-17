import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    app_title: str = "FastAPI OpenFGA Project"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./app.db"
    
    # Auth0 FGA Configuration
    auth0_fga_store_id: str = ""
    auth0_fga_client_id: str = ""
    auth0_fga_client_secret: str = ""   
    auth0_fga_authorization_model_id: str = ""
    auth0_fga_api_token_issuer: str = ""
    auth0_fga_api_audience: str = ""
    auth0_fga_api_url: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()