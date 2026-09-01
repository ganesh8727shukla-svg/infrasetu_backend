from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InfraSetu API"
    environment: str = "development"

    database_url: str = (
        "postgresql+psycopg://infrasetu:infrasetu@localhost:5432/infrasetu"
    )

    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = (
        "http://localhost:8080,"
        "http://127.0.0.1:8080,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:3000"
    )

    upload_dir: str = "storage/uploads"

    # Backend is running on port 8001
    public_base_url: str = "http://localhost:8001"

    max_upload_bytes: int = 10 * 1024 * 1024

    allowed_upload_types: str = (
        "image/jpeg,image/png,image/webp"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            x.strip()
            for x in self.cors_origins.split(",")
            if x.strip()
        ]

    @property
    def allowed_upload_type_list(self) -> set[str]:
        return {
            x.strip().lower()
            for x in self.allowed_upload_types.split(",")
            if x.strip()
        }


settings = Settings()