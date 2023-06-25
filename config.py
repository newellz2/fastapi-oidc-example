from pydantic import (
    BaseSettings,
    SecretStr
)


class Settings(BaseSettings):
    DEBUG: bool = False
    BASE_URL: str
    SECRET_KEY: SecretStr
    OIDC_METADATA_URL: str
    OIDC_CLIENT_ID: str
    OIDC_CLIENT_SECRET: SecretStr
    OIDC_SCOPE: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
