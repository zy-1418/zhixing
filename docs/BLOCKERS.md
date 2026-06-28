# Cloud 环境阻塞记录

本次自动化运行环境为 Cursor Cloud，无法访问开发者本机服务与部分 SDK。按工作流规则，以下能力采用占位实现并继续推进：

| 依赖 | 验证结果 | 处理 |
|------|----------|------|
| Docker / docker compose | `docker: command not found` | 保留并扩展 `infra/docker-compose.yml`，无法实际启动中间件 |
| Flutter SDK | `flutter: command not found` | 手写 `apps/mobile` Flutter 壳与页面占位，无法执行 `flutter create/run/analyze` |
| MetaGPT-X `127.0.0.1:8000` | Cloud 无法访问本机服务 | `/api/v1/tasks/sop` 在连接失败时返回 `metagpt-unavailable-*` 占位 job_id |
| Dify | 未配置 `DIFY_API_KEY`，且未启动自托管服务 | `/api/v1/dify/*` 返回 blocked/echo 占位响应 |
| Redis / Meilisearch / Qdrant / Neo4j / Medusa | 中间件未启动 | 暴露 API 契约与配置项，返回 placeholder/blocked 状态 |

恢复本机验收时建议顺序：

1. 安装 Docker 与 Flutter stable。
2. `cd infra && docker compose up -d`。
3. 启动本机 MetaGPT-X API：`METAGPT_X_API=http://127.0.0.1:8000`。
4. 配置 `DIFY_API_KEY` 并启动 Dify。
5. 运行后端导入、OpenAPI、Flutter analyze 与端到端任务提交检查。
