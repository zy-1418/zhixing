# 知行自动实施 Release

## 完成范围

- P0：保留 Docker Compose、MetaGPT Bridge、Flutter 五 Tab 壳与自动续跑状态文件。
- P1：补齐 FastAPI 鉴权、schema、工作区/对话导出、笔记 CRUD、Dify 代理、任务日历、MetaGPT WS 日志代理与 QA optimize。
- P1 Flutter：在无 SDK 的 Cloud 中手写工作区树、对话入口、SOP 提交与纯文档笔记编辑器占位。
- P2：提供 OpenIM、广场 Feed、赞/踩理由、结构化辩论、插件市场、搜索与个人主页 API 形状。
- P3：提供知识图谱抽取、sigma payload、好友 AI 与 AI 小程序占位 API。
- P4：提供 Medusa 订单/钱包占位 API，记录桌面端与离线缓存落点。

## Cloud 阻塞

Cloud 环境缺少 Docker、Flutter、本机 MetaGPT-X 与 Dify/LLM 配置。相关步骤已按规则用占位实现完成，并记录在 `docs/BLOCKERS.md`。

## 验证

- Python 后端导入、编译与 OpenAPI 路径检查作为 Cloud 轻量验证。
- Flutter/Docker/MetaGPT/Dify 需在具备依赖的本机环境复验。

## 后续建议

1. 本机启动 `infra/docker-compose.yml` 并执行 Alembic migration。
2. 启动 MetaGPT-X 后验证 `POST /api/v1/tasks/sop` 与 `/tasks/metagpt/{job_id}/logs`。
3. 配置 Dify「林」Agent，验证 `/api/v1/dify/chat` 的 @笔记上下文注入。
4. 安装 Flutter SDK 后运行 `flutter analyze` 与真机/模拟器冒烟测试。
