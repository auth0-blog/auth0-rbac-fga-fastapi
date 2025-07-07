from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application Configuration
    app_title: str = "FastAPI OpenFGA Project"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # OpenFGA Configuration
    openfga_api_url: str = "http://localhost:8080"
    openfga_store_id: str = ""
    openfga_authorization_model_id: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()