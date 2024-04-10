from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str
    environment: str
    host: str
    port: int
    reload: bool

    class Config:
        env_file = ".env"

settings = Settings()