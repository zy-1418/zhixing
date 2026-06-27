# Dify 自托管与「林」Agent 配置

## 启动方式

Dify 体积较大，保持为独立 vendor 服务，不放入 `infra/docker-compose.yml` 的默认启动链路。

```powershell
powershell -File scripts/clone-deps.ps1
cd vendor/dify/docker
docker compose up -d
```

启动后在 Dify 控制台创建应用，并把 API 地址与密钥写入知行 API 环境：

```env
DIFY_API_URL=http://127.0.0.1:5001/v1
DIFY_API_KEY=app-***
```

## 「林」Agent 建议

- 类型：Chatflow / Agent Chat
- 名称：林
- 角色：知行里的学习、研究、写作助手
- 能力：
  - 普通对话
  - PDF / 笔记 RAG
  - 接收 `zhixing_note_context` 作为 @引用上下文
  - 对轻量表格、摘要、对比清单直接生成结果

## 知行 API 映射

| 知行 API | Dify API | 说明 |
|----------|----------|------|
| `POST /api/v1/dify/chat` | `/chat-messages` | 代理对话，支持 `note_ids[]` 注入笔记上下文 |
| `POST /api/v1/dify/upload` | `/files/upload` | 上传 PDF/图片等文件 |

未配置 `DIFY_API_KEY` 时，代理会返回 `503`，这是 Cloud 环境下的预期占位行为。
