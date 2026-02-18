"""
Configuration management for the Ride-Hailing Platform.
Loads environment variables and provides typed configuration objects.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="Ride-Hailing Platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(..., alias="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # PostgreSQL
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ride_hailing", alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    
    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    
    # MongoDB
    mongodb_host: str = Field(default="localhost", alias="MONGODB_HOST")
    mongodb_port: int = Field(default=27017, alias="MONGODB_PORT")
    mongodb_db: str = Field(default="ride_hailing_location", alias="MONGODB_DB")
    mongodb_user: str = Field(default="", alias="MONGODB_USER")
    mongodb_password: str = Field(default="", alias="MONGODB_PASSWORD")
    
    # JWT
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Payment Gateways
    razorpay_key_id: str = Field(default="", alias="RAZORPAY_KEY_ID")
    razorpay_key_secret: str = Field(default="", alias="RAZORPAY_KEY_SECRET")
    paytm_merchant_id: str = Field(default="", alias="PAYTM_MERCHANT_ID")
    paytm_merchant_key: str = Field(default="", alias="PAYTM_MERCHANT_KEY")
    
    # SMS Gateway
    twilio_account_sid: str = Field(default="", alias="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(default="", alias="TWILIO_AUTH_TOKEN")
    twilio_phone_number: str = Field(default="", alias="TWILIO_PHONE_NUMBER")
    
    # Google Maps
    google_maps_api_key: str = Field(default="", alias="GOOGLE_MAPS_API_KEY")
    
    # Indore City Boundaries
    indore_lat_min: float = Field(default=22.6, alias="INDORE_LAT_MIN")
    indore_lat_max: float = Field(default=22.8, alias="INDORE_LAT_MAX")
    indore_lon_min: float = Field(default=75.7, alias="INDORE_LON_MIN")
    indore_lon_max: float = Field(default=75.9, alias="INDORE_LON_MAX")
    
    # Ride Matching
    initial_search_radius_km: float = Field(default=5.0, alias="INITIAL_SEARCH_RADIUS_KM")
    search_radius_expansion_km: float = Field(default=2.0, alias="SEARCH_RADIUS_EXPANSION_KM")
    match_timeout_seconds: int = Field(default=120, alias="MATCH_TIMEOUT_SECONDS")
    
    # Fare Configuration
    base_fare: float = Field(default=30.0, alias="BASE_FARE")
    per_km_rate: float = Field(default=12.0, alias="PER_KM_RATE")
    fare_protection_threshold: float = Field(default=0.20, alias="FARE_PROTECTION_THRESHOLD")
    
    @property
    def postgres_url(self) -> str:
        """Generate PostgreSQL connection URL."""
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Generate Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def mongodb_url(self) -> str:
        """Generate MongoDB connection URL."""
        if self.mongodb_user and self.mongodb_password:
            return f"mongodb://{self.mongodb_user}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
