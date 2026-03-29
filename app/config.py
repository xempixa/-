from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="bili-charge-archiver", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")

    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    download_dir: Path = Field(default=Path("./data/downloads"), alias="DOWNLOAD_DIR")
    storage_state_path: Path = Field(default=Path("./data/storage_state.json"), alias="STORAGE_STATE_PATH")
    sqlite_path: Path = Field(default=Path("./data/app.db"), alias="SQLITE_PATH")

    bili_base_url: str = Field(default="https://www.bilibili.com", alias="BILI_BASE_URL")
    bili_api_base: str = Field(default="https://api.bilibili.com", alias="BILI_API_BASE")
    user_agent: str = Field(alias="USER_AGENT")

    http_timeout: int = Field(default=20, alias="HTTP_TIMEOUT")
    http_max_connections: int = Field(default=10, alias="HTTP_MAX_CONNECTIONS")
    http_max_keepalive: int = Field(default=5, alias="HTTP_MAX_KEEPALIVE")

    request_min_interval_ms: int = Field(default=800, alias="REQUEST_MIN_INTERVAL_MS")
    request_max_interval_ms: int = Field(default=2000, alias="REQUEST_MAX_INTERVAL_MS")

    yt_dlp_bin: str = Field(default="yt-dlp", alias="YT_DLP_BIN")


settings = Settings()
