# 性能与压测

## 当前状态

Cloud 环境无法启动 Docker 中间件与 Flutter，无法进行端到端压测。本阶段交付压测入口与验收建议，作为 P4 完成占位。

## 建议压测范围

- FastAPI：
  - `/api/v1/search`
  - `/api/v1/tasks`
  - `/api/v1/dify/chat`
  - `/api/v1/social/posts`
- 中间件：
  - PostgreSQL 连接池。
  - Redis 优先级队列。
  - Meilisearch 索引延迟。
  - Qdrant 用户分库查询。

## 本机命令建议

```bash
python -m uvicorn main:app --port 8080
hey -z 30s -c 20 http://127.0.0.1:8080/health
```

## 移动端性能关注

- WebView 静态页按需加载。
- 图谱/画布/PDF 大资源不进入首屏。
- 离线笔记缓存限制为最近 23 篇。
