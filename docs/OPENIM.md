# OpenIM 集成设计

Phase 2 将 OpenIM 用于好友、群聊与团队协作。当前仓库提供 API 契约与 Flutter 入口，占位端点为 `GET /api/v1/openim/status`，并保留旧路径 `GET /api/v1/extensions/openim/status` 作为兼容别名。

## 边界

- Flutter 端使用 OpenIM SDK 负责实时消息、好友列表、群组会话。
- 知行 API 负责：
  - 用户 ID 与 OpenIM userID 映射。
  - 好友 AI、工作区邀请与团队权限同步。
  - 审计与举报入口。
- OpenIM 服务端独立部署，不进入 MetaGPT-X 执行环境。

## 推荐数据流

```text
Flutter 好友页
  -> OpenIM SDK 登录/收发消息
  -> Zhixing API 查询用户资料、好友 AI 配置、团队工作区权限
```

## 后续实现清单

- [ ] `openim_users` 映射表。
- [ ] 服务端 token 签发代理。
- [ ] 群聊与 workspace_folders 权限绑定。
- [ ] 消息引用笔记/任务时写入工作区上下文。
