from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    vonage_application_id: str
    vonage_private_key_path: str
    verify_brand_name: str = "Hello World"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
