from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Zhixing API"
    debug: bool = True
    database_url: str = (
        "postgresql+asyncpg://zhixing:zhixing_dev@127.0.0.1:5432/zhixing"
    )
    secret_key: str = "zhixing-dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    metagpt_x_api: str = "http://127.0.0.1:8000"
    metagpt_root: str = r"G:\MetaGPT"
    metagpt_stub_on_unreachable: bool = True
    redis_url: str = "redis://localhost:6379/0"
    dify_api_base: str = "http://127.0.0.1:5001/v1"
    dify_api_key: str = ""
    meili_url: str = "http://127.0.0.1:7700"
    qdrant_url: str = "http://127.0.0.1:6333"
    neo4j_url: str = "bolt://127.0.0.1:7687"
    medusa_api_url: str = "http://127.0.0.1:9000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
