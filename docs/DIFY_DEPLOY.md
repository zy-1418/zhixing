# Dify 自托管与「林」Agent 配置

Phase 1 将 Dify 作为知行日常对话、PDF 问答与 @引用笔记的 RAG 层。Cloud 环境无法启动完整 Dify，本页记录本机部署与 API 代理契约。

## 启动

1. 使用 `scripts/clone-deps.ps1` 拉取 `vendor/dify`。
2. 进入 `vendor/dify/docker`，按 Dify 官方文档复制 `.env.example`。
3. 启动 Dify：

```bash
docker compose up -d
```

4. 在知行 API `.env` 中配置：

```env
DIFY_API_URL=http://127.0.0.1:5001
DIFY_API_KEY=<林 Agent API Key>
DIFY_USER=zhixing-local
```

## 「林」Agent 建议

- 类型：Chat App + Knowledge Base。
- 系统提示词：你是知行的个人知识助理「林」，优先引用用户笔记和工作区上下文回答。
- 输入变量：
  - `note_context`：由知行 API 将 `note_ids` 对应 blocks 拼接后注入。
  - `workspace_context`：当前文件夹、任务或对话摘要。
- 文件能力：启用 PDF / Markdown 上传，供 `/api/v1/dify/upload` 转发。

## API 代理

| 知行 API | Dify API | 行为 |
|----------|----------|------|
| `POST /api/v1/dify/chat` | `/v1/chat-messages` | 拼接 @引用笔记后阻塞式返回 |
| `POST /api/v1/dify/upload` | `/v1/files/upload` | 原样转发文件流 |

未配置 `DIFY_API_KEY` 时，路由返回 `blocked=true` 与 echo payload，便于 Flutter 与后端联调。
