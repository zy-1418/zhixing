from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Zhixing API"
    debug: bool = True
    database_url: str = (
        "postgresql+asyncpg://zhixing:zhixing_dev@127.0.0.1:5432/zhixing"
    )
    jwt_secret: str = "zhixing-dev-secret-change-me"
    jwt_issuer: str = "zhixing-api"
    access_token_minutes: int = 60 * 24 * 7
    dify_api_url: str = "http://127.0.0.1:5001/v1"
    dify_api_key: str = ""
    redis_url: str = "redis://127.0.0.1:6379/0"
    metagpt_x_api: str = "http://127.0.0.1:8000"
    metagpt_root: str = r"G:\MetaGPT"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
