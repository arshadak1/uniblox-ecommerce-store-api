"""
Configuration module for the uniblox-ecommerce-store.
Uses `pydantic-settings` for environment variable management.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Uniblox E-commerce API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    API_PREFIX: str = "/api/v1"
    
    NTH_ORDER_DISCOUNT: int = 7
    DISCOUNT_PERCENTAGE: float = 10
    DISCOUNT_CODE_PREFIX: str = "SAVE10"
    DISCOUNT_CODE_LENGTH: int = 8

    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

settings = Settings()
