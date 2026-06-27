# P2-P4 占位实现说明

按照自动续跑规则，Cloud 中不可用的外部系统先提供稳定 API 形状与文档，后续在具备服务的环境替换实现。

## P2 社交与工作流

- 广场 Feed：`/api/v1/social/posts`
- 赞/踩需理由：`/api/v1/social/posts/{post_id}/votes`
- 结构化辩论：`/api/v1/social/debates`
- OpenIM：`/api/v1/im/*`
- 插件市场：`/api/v1/market/agents`
- 搜索：`/api/v1/search`，Cloud 下使用 PostgreSQL fallback，真实部署切换 Meilisearch。
- React Flow：移动端可用 WebView 嵌入静态工作流页，当前保留接口与文档。

## P3 知识图谱与 AI 小程序

- Neo4j 抽取占位：`/api/v1/graph/relations/extract`
- sigma.js 数据：`/api/v1/graph/sigma`
- 好友 AI 蒸馏：`/api/v1/graph/friend-ai/chat`
- AI 小程序生成：`/api/v1/graph/mini-programs/generate`
- tldraw / 双联 PDF：Flutter WebView 集成点保留，Cloud 无法构建前端包。

## P4 电商与桌面

- Medusa 占位：`/api/v1/commerce/*`
- 桌面端：Flutter desktop 优先，Tauri 作为 WebView 备选。
- 离线缓存：移动端后续使用本地 SQLite/文件缓存保留最近 23 篇笔记。
