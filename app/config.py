from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cocktaildb_api_key: str = "1"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./cocktails.db"
    database_url_sync: str = "sqlite:///./cocktails.db"

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/callback"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7

    session_secret: str = ""

    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    assistant_history_limit: int = 10
    assistant_rate_limit_per_min: int = 10

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cocktaildb_base_url(self) -> str:
        return f"https://www.thecocktaildb.com/api/json/v1/{self.cocktaildb_api_key}/"


settings = Settings()
