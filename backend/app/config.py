from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://usuario:contraseña@localhost:5432/finanzapp"
    secret_key: str = "cambia-esta-clave-en-produccion"
    algorithm: str = "HS256"
    access_token_expire_days: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
