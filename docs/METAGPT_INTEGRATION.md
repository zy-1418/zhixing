# MetaGPT-X 嵌入知行 — 详细方案

## 现状摘要（G:\MetaGPT）

| 项 | 状态 |
|----|------|
| MetaGPT-X API | ✅ FastAPI `:8000`，`/api/v1/projects/sop` |
| 任务队列 | ✅ 单 worker SQLite `metagpt_x_jobs.db` |
| SOP 流水线 | ✅ PM→原型→OSS Scout→开发→QA |
| LangGraph | ✅ 仅 QA 子图 `qa_graph.py` |
| Flutter | ❌ 无；偏微信小程序 |
| Dify | ❌ 无原生集成 |

**结论**：MetaGPT-X 作为 **「后台代码工厂」** 嵌入，不替代 Dify 对话层。

---

## 集成架构

```
Flutter 布置任务
    ↓
知行 API  POST /tasks/sop
    ↓ 组装 idea + 注入 spec
MetaGPT Bridge  POST :8000/api/v1/projects/sop
    ↓ 排队
MetaGPT-X Worker  sop_pipeline → Team → workspace/
    ↓
知行 API  轮询/WS 更新 tasks 表
    ↓
Flutter 工作区 显示任务状态 + 产物链接
```

---

## 任务类型 → SOP 模板

| 知行 UI | workflow_type | MetaGPT idea 前缀 |
|---------|---------------|-------------------|
| 研究型 | `research` | `【研究流水线】检索→初稿→审查→校验。` |
| 写作型 | `writing` | `【写作流水线】大纲→起草→润色→校对。` |
| 检索型 | `search` | `【检索流水线】检索→汇总→归档。` |
| 自定义 | `custom` | 用户一句话原文 |

实现位置：`services/metagpt-bridge/templates.py`

---

## 上下文注入（笔记 → SOP）

1. 用户在工作区选中文件夹内笔记
2. 知行 API 读取 note 内容，写入临时 spec：

```
G:\MetaGPT\projects\{task_slug}\specs\001-mvp\spec.md
```

3. 调用 SOP 时 `skip_dev=false`，idea 中引用 spec 路径

Bridge 代码见 `services/metagpt-bridge/context_builder.py`

---

## API 映射表

| 知行 API | MetaGPT-X API | 说明 |
|----------|---------------|------|
| `POST /tasks/sop` | `POST /api/v1/projects/sop` | 创建任务 |
| `GET /tasks/{id}` | `GET /api/v1/projects/{id}` | 状态 |
| `GET /tasks/queue` | `GET /api/v1/queue` | 排队 |
| `WS /tasks/{id}/logs` | `WS /api/v1/projects/{id}/ws` | 日志代理 |
| `POST /tasks/{id}/retry` | `POST /api/v1/projects/{id}/optimize` | QA 修复 |

---

## 优先级策略

MetaGPT-X **无原生优先级**。知行侧实现：

| 优先级 | 行为 |
|--------|------|
| 高 | 插入 Redis 队首；若 worker 空闲立即提交 |
| 中 | FIFO |
| 低 | 延迟队列，worker 空闲 >5min 才消费 |

实现：`services/api/routers/tasks.py` + Redis LIST

---

## 与 Dify 分工

| 场景 | Dify | MetaGPT-X |
|------|------|-----------|
| 日常对话、@引用 | ✅ | ❌ |
| PDF 问答 | ✅ RAG | ❌ |
| 生成 CSV/对比表（轻量） | ✅ | ❌ |
| 多文件项目代码生成 | ❌ | ✅ |
| SOP 原型+OSS Scout | ❌ | ✅ |
| pytest QA 修复环 | ❌ | ✅ |

---

## 启动依赖

1. `~/.metagpt/config2.yaml` 配置 LLM
2. `G:\MetaGPT\scripts\start_metagpt_x_api.ps1`
3. 环境变量：

```env
METAGPT_X_API=http://127.0.0.1:8000
METAGPT_ROOT=G:\MetaGPT
```

---

## 待补 MetaGPT 能力（可选 PR 回上游）

- [ ] SOP API 支持 `priority` 字段
- [ ] SOP API 支持 `context_files[]` 直接上传
- [ ] MCP `metagpt_create_sop` 与知行 task_id 双向绑定
- [ ] Webhook：`job completed` 回调知行 API

---

## Phase 0 已交付代码

- `services/metagpt-bridge/client.py` — HTTP 客户端
- `services/metagpt-bridge/templates.py` — 工作流模板
- `services/api/routers/tasks.py` — 转发路由
