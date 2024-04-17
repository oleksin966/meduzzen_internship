from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str
    environment: str
    host: str
    port: int
    reload: bool

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    redis_host: str
    redis_port: int

    PROD: str = "INFO"

    class Config:
        env_file = ".env"

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        #return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@db:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self):
        return f"redis://{self.redis_host}:{self.redis_port}"
        # return f"redis://redis:{self.redis_port}"

settings = Settings()
