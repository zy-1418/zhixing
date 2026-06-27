# OpenIM 集成设计

## 目标

P2 的好友、群聊、团队协作由 OpenIM 提供底层 IM 能力，知行 API 只负责：

- 绑定知行用户 ID 与 OpenIM 用户
- 签发/刷新移动端连接 token
- 在工作区内记录与任务、笔记相关的会话入口

## 当前实现

- `GET /api/v1/im/status`：返回 OpenIM 占位状态
- `POST /api/v1/im/tokens`：返回占位 token，保持移动端接口契约

Cloud 环境无法启动 OpenIM 服务，因此真实 SDK 初始化留给本机/部署环境验证。

## 后续替换点

1. 在服务端配置 OpenIM admin secret。
2. 注册用户时同步创建 OpenIM user。
3. `/im/tokens` 调用 OpenIM REST API 签发真实 token。
4. Flutter 好友页接入 OpenIM Flutter SDK。
