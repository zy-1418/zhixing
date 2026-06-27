# 知行（Zhixing）开源技术栈 — 终版选型

> 基于视频 Demo「知行 v0.5」功能拆解 + 本地 MetaGPT-X 能力对齐  
> 原则：**能自托管、能嵌入、少重复造轮子**

## 总览

| 层级 | 选型 | 仓库 | 角色 |
|------|------|------|------|
| 移动端 | **Flutter 3.x** | [flutter/flutter](https://github.com/flutter/flutter) | iOS/Android/Web/桌面一套代码 |
| 业务 API | **FastAPI** | [tiangolo/fastapi](https://github.com/tiangolo/fastapi) | 知行网关，统一鉴权/路由 |
| AI 对话+RAG | **Dify** | [langgenius/dify](https://github.com/langgenius/dify) | 用户侧「林」助手、@引用、插件市场 |
| 代码工厂 | **MetaGPT-X** | `G:\MetaGPT\metagpt-x`（已有） | 工作流/SOP/多 Agent 编码任务 |
| 任务队列 | **MetaGPT-X Queue** + **Redis** | 内置 + [redis/redis](https://github.com/redis/redis) | 重型编码单 worker；轻量任务 Redis |
| 数据库 | **PostgreSQL** + **Supabase 模式** | [supabase/supabase](https://github.com/supabase/supabase) | 用户/笔记/社交（可 Docker 自托管） |
| 向量检索 | **Qdrant** | [qdrant/qdrant](https://github.com/qdrant/qdrant) | 笔记/PDF 嵌入（Dify 可共用） |
| 全文搜索 | **Meilisearch** | [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch) | 广场热搜/作者/话题 |
| 笔记画布 | **tldraw** | [tldraw/tldraw](https://github.com/tldraw/tldraw) | 无限画布（WebView 嵌入 Flutter） |
| 块编辑器 | **AppFlowy Editor** 思路 | [AppFlowy-IO/appflowy-editor](https://github.com/AppFlowy-IO/appflowy-editor) | 纯文档/双联阅读 |
| 工作流 UI | **React Flow** | [xyflow/xyflow](https://github.com/xyflow/xyflow) | 节点编排（Web 组件 → Flutter WebView） |
| 知识图谱 | **Neo4j** + **sigma.js** | [neo4j/neo4j](https://github.com/neo4j/neo4j) | 广场图谱/论点演化（Phase 3） |
| IM 社交 | **OpenIM** | [openimsdk/open-im-server](https://github.com/openimsdk/open-im-server) | 好友/群聊/团队（Phase 2） |
| 电商 | **Medusa** | [medusajs/medusa](https://github.com/medusajs/medusa) | 订单/购物车/钱包（Phase 4） |
| 文档解析 | **Unstructured** | [Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured) | PDF/图片 OCR 管道 |
| Agent 编排（补充） | **LangGraph** | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 与 MetaGPT qa_graph 对齐 |

## 不选 / 降级说明

| 候选 | 决定 | 原因 |
|------|------|------|
| AFFiNE 整体 fork | ❌ 仅借鉴 | 单体过大，与 Flutter 栈不匹配 |
| CrewAI 作主引擎 | ❌ 降级为可选 | MetaGPT-X 已有多 Agent + SOP |
| 纯 LangChain 自搭 RAG | ❌ | Dify 已封装；MetaGPT 自带 rag/ |
| React Native | ❌ | 画布/图谱 Flutter 生态更合适 |

## MetaGPT 嵌入定位

```
用户「布置任务」→ 知行 API → MetaGPT-X POST /api/v1/projects/sop
                              → 单 worker 队列执行 SOP
                              → 产物写入 projects/{slug}/workspace/
                              → 知行工作区文件树展示 + 导出
```

MetaGPT **不负责**：社交、笔记 UI、电商、IM。  
MetaGPT **负责**：研究型/写作型/检索型工作流的 **代码与自动化产出**。

## 目录与 vendor 策略

```
zhixing/
  apps/mobile/          # Flutter
  services/api/         # 知行 FastAPI 网关
  services/metagpt-bridge/
  vendor/
    dify/               # git shallow clone
    tldraw/             # git shallow clone（Web 组件参考）
  infra/
    docker-compose.yml  # postgres, redis, qdrant, meilisearch, dify
```

MetaGPT 不重复 clone，通过环境变量 `METAGPT_X_API=http://127.0.0.1:8000` 引用 `G:\MetaGPT`。

## 版本锁定（Phase 0）

- Python 3.11（MetaGPT 要求 <3.12）
- Flutter stable channel
- Dify latest release tag（vendor 内 pin）
- Node 20 LTS（tldraw / dify 构建）
