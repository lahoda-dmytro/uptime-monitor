from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_db: str = "uptime_monitor"
    postgres_user: str = "postgres"
    postgres_password: str = "secure_password_here"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    ping_interval_seconds: int = 60

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    class Config:
        env_file = ".env"

settings = Settings()
