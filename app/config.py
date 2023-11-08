from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # DB
    db_hostname: str
    db_password: str
    db_username: str
    db_name: str
    db_port: str

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int 

    model_config = SettingsConfigDict(env_file=f"{os.path.dirname(os.path.abspath(__file__))}/.env")

settings = Settings() # type: ignore
