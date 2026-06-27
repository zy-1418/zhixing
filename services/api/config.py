from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Zhixing API"
    debug: bool = True
    database_url: str = (
        "postgresql+asyncpg://zhixing:zhixing_dev@127.0.0.1:5432/zhixing"
    )
    auth_secret_key: str = "zhixing-dev-secret-change-me"
    access_token_expires_minutes: int = 60 * 24 * 7
    dify_api_base_url: str = "http://127.0.0.1/v1"
    dify_api_key: str | None = None
    openim_api_base_url: str = "http://127.0.0.1:10002"
    openim_admin_token: str | None = None
    meili_host: str = "http://127.0.0.1:7700"
    meili_master_key: str = "zhixing_meili_dev_key"
    neo4j_uri: str = "bolt://127.0.0.1:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "zhixing_graph_dev"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: str | None = None
    medusa_backend_url: str = "http://127.0.0.1:9000"
    medusa_api_key: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    metagpt_x_api: str = "http://127.0.0.1:8000"
    metagpt_root: str = r"G:\MetaGPT"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
