# Cloud 环境阻塞记录

本文件记录 Cursor Cloud 环境无法直接验证、但已按占位实现继续推进的事项。

## Docker

- 状态：`docker` / `docker compose` 命令不可用。
- 影响：无法在 Cloud 中执行 `cd infra && docker compose config` 或启动 PostgreSQL、Redis、Qdrant、Meilisearch、Dify。
- 处理：保留 `infra/docker-compose.yml`，通过代码审阅和后续本机 Docker 验证完成闭环。

## Flutter

- 状态：`flutter` 命令不可用。
- 影响：无法执行 `flutter create`、`flutter analyze`、`flutter run`。
- 处理：手写 `apps/mobile` 五 Tab 壳、工作区/任务/对话/笔记占位 UI；需本机 Flutter SDK 复验。

## MetaGPT-X

- 状态：Cloud 无法访问宿主机 `127.0.0.1:8000` MetaGPT-X。
- 影响：无法完成真实 `POST /api/v1/tasks/sop` 端到端联调。
- 处理：保留 FastAPI bridge、任务落库、WS 日志代理和 QA optimize 路由；本机启动 MetaGPT-X 后复验。

## Dify / LLM

- 状态：Cloud 未配置 `DIFY_API_KEY`，也无法启动 Dify 自托管容器。
- 影响：对话/RAG 只能验证代理路由结构，不能验证真实 LLM 输出。
- 处理：`/api/v1/dify/*` 在未配置密钥时返回明确 503；见 `docs/DIFY_SELF_HOSTING.md`。
