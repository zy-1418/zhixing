# Dify 自托管与「林」Agent 配置

## Cloud Agent 状态

当前 Cloud 环境缺少 Docker，无法执行 Dify 自托管启动。代码侧已交付：

- `services/api/routers/dify.py`：知行 API 到 Dify 的代理路由。
- `.env.example`：`DIFY_API_BASE_URL` 与 `DIFY_API_KEY` 配置位。
- `docs/BLOCKERS.md`：记录 Cloud 环境无法验证 Docker/Dify 的原因。

## 本机启动步骤

1. 拉取 vendor：

   ```powershell
   powershell -File scripts/clone-deps.ps1
   ```

2. 启动知行基础中间件：

   ```powershell
   cd infra
   docker compose up -d postgres redis qdrant meilisearch
   ```

3. 启动 Dify：

   ```powershell
   cd vendor/dify/docker
   copy .env.example .env
   docker compose up -d
   ```

4. 在知行 API `.env` 中配置：

   ```env
   DIFY_API_BASE_URL=http://127.0.0.1/v1
   DIFY_API_KEY=<林 Agent App API Key>
   ```

## 「林」Agent 建议配置

- 类型：Chat Assistant。
- 名称：林。
- 开场白：`你好，我是林。你可以 @ 引用知行笔记，或上传资料让我帮你整理、检索和规划任务。`
- 编排说明：
  - 优先使用用户通过 `note_ids` 注入的知行笔记上下文。
  - 回答中保留引用来源：`@note_id`、文件名或工作区路径。
  - 轻量总结、问答、表格整理在 Dify 内完成。
  - 多文件代码生成或重型 SOP 任务，引导用户使用知行「布置任务」提交给 MetaGPT-X。
- 工具建议：
  - Knowledge / Dataset：接入用户笔记与 PDF 的向量库。
  - File upload：允许 PDF、Markdown、文本文件。
  - HTTP Tool：后续可回调知行 API 写入笔记或任务。

## 代理接口

- `POST /api/v1/dify/chat`：转发到 Dify `/chat-messages`，支持 `note_ids` 注入。
- `POST /api/v1/dify/upload`：转发到 Dify `/files/upload`，Cloud 未配置 Key 时返回占位响应。
