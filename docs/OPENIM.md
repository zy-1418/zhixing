# OpenIM 集成占位设计

Phase 2 的好友、群聊、团队能力通过 OpenIM 承接。

## 当前交付

- `GET /api/v1/im/status` 返回 OpenIM 集成状态。
- Flutter 好友 Tab 增加 OpenIM、好友 AI、AI 小程序入口。
- 暂不在 Cloud 内启动 OpenIM 服务，避免引入大型外部部署。

## 后续接入点

1. 部署 OpenIM server 并配置移动端 SDK。
2. 在知行 API 内保存 `user_id -> openim_user_id` 映射。
3. 登录成功后由后端签发 OpenIM token。
4. Flutter 好友 Tab 调用 SDK 拉取好友、群聊与未读消息。

## 安全边界

OpenIM token 只由服务端签发；移动端不保存 OpenIM 管理密钥。
