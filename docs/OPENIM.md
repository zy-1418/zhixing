# OpenIM 集成设计

## 目标

P2 社交能力使用 OpenIM 承担好友、群聊和团队消息。知行后端只做账号绑定、Token 颁发和业务权限校验，移动端通过 OpenIM SDK 直连 OpenIM 服务。

## 边界

- 知行 API：
  - 映射知行 `users.id` 到 OpenIM `userID`。
  - 通过 `services/api/routers/im.py` 提供 bridge 占位接口。
  - 校验好友、群聊和团队空间的知行业务权限。
- OpenIM：
  - 负责消息收发、离线消息、会话列表、群成员状态。
  - 不保存知行笔记、任务或工作区内容。

## 本机配置

```env
OPENIM_API_BASE_URL=http://127.0.0.1:10002
OPENIM_ADMIN_TOKEN=<OpenIM admin token>
```

Cloud 环境未运行 OpenIM，也未配置 admin token，因此 IM bridge 会返回占位响应。

## Bridge API

- `GET /api/v1/im/health`
  - 已配置 OpenIM 时代理健康检查。
  - 未配置时返回 placeholder。
- `POST /api/v1/im/users/token`
  - 输入：`user_id`、`nickname`、`face_url`。
  - 输出：OpenIM token 或 Cloud placeholder。

## 后续接入点

1. 注册/登录后同步创建 OpenIM 用户。
2. Flutter 好友页集成 OpenIM SDK。
3. 工作区任务、笔记分享时创建临时群或团队空间。
4. P2 Feed 与个人主页复用好友关系数据做可见性控制。
