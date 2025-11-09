from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This tells Pydantic to expect these variables from the .env file
    DATABASE_URL: str
    PORT: int = 8000
    SECRET_KEY: str = "4b2d3c09a723e532c44255a1995b63d3ff9f6a71c608e8a741bb5f9dc3081a13"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )

# Create a single instance to be imported by other files
settings = Settings()