# Dify 自托管与「林」Agent 配置

## 当前状态

Cloud 环境未拉起 Dify，自托管部署以文档和 API 占位交付：

- `POST /api/v1/dify/chat-messages`
- `POST /api/v1/dify/files/upload`
- `GET /api/v1/dify/agent/lin`

未配置 `DIFY_API_KEY` 时，上述端点返回本地占位响应。

## 本地配置

1. 按 `vendor/dify` 官方 docker compose 启动 Dify。
2. 创建应用「林」：
   - 类型：Chatflow 或 Agent
   - 能力：RAG、工具调用、笔记 ID 引用
   - 输入变量：`referenced_note_ids`
3. 在 `.env` 写入：

```env
DIFY_API_BASE=http://127.0.0.1:5001/v1
DIFY_API_KEY=<林 Agent API Key>
```

4. 重启 `services/api`。

## @引用笔记约定

移动端传入 `note_ids`，API 会转成 Dify inputs：

```json
{
  "referenced_note_ids": ["note-uuid"]
}
```
