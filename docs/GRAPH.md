# 知识图谱与 Neo4j 管线

## 已交付

- `infra/docker-compose.yml` 增加 `neo4j:5-community` 服务。
- `services/api/routers/graph.py` 提供笔记关系抽取占位管线：
  - `POST /api/v1/graph/notes/{note_id}/extract`
  - `GET /api/v1/graph/preview`

## 抽取策略

P3 初版以轻量规则抽取笔记 blocks 中的 `#主题` 与 `@实体`，生成：

- Note 节点。
- Entity 节点。
- `MENTIONS` 关系。

后续可接入 Dify/LLM 做实体归一化、关系分类和置信度评分，再写入 Neo4j。

## Cloud 限制

当前 Cloud 环境没有 Docker，无法启动 Neo4j。API 返回抽取结果和 Neo4j skipped 状态，便于前端先联调图谱展示。
