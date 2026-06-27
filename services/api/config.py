from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Zhixing API"
    debug: bool = True
    database_url: str = (
        "postgresql+asyncpg://zhixing:zhixing_dev@127.0.0.1:5432/zhixing"
    )
    auth_secret_key: str = "zhixing-dev-secret-change-me"
    access_token_expires_minutes: int = 60 * 24 * 7
    metagpt_x_api: str = "http://127.0.0.1:8000"
    metagpt_root: str = r"G:\MetaGPT"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
