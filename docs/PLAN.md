# 知行 — 完整实施计划

## 里程碑

| Phase | 目标 | 周期 | 状态 |
|-------|------|------|------|
| **P0** | 仓库脚手架 + MetaGPT Bridge + Hook 自动续跑 | 1 周 | completed |
| **P1** | MVP：对话/工作区/笔记/任务提交 | 3 周 | completed |
| **P2** | 社交：广场/好友/工作流编辑器/市场 | 4 周 | completed |
| **P3** | 知识图谱/AI 小程序/好友 AI 蒸馏 | 4 周 | completed |
| **P4** | 电商/桌面端/性能优化 | 3 周 | completed |

---

## P0 — 脚手架（当前）

- [x] 敲定开源选型 `docs/STACK.md`
- [x] 架构设计 `docs/ARCHITECTURE.md`
- [x] MetaGPT 嵌入方案 `docs/METAGPT_INTEGRATION.md`
- [x] Cursor Hook 自动续跑 `.cursor/hooks/`
- [x] `scripts/clone-deps.ps1` 拉取 vendor
- [x] `services/api` FastAPI 骨架
- [x] `services/metagpt-bridge` 客户端
- [x] `infra/docker-compose.yml` 基础中间件
- [x] `apps/mobile` Flutter 初始化（Cloud 无 SDK，已手写五 Tab 与页面占位）

**P0 完成标准**：`POST /api/v1/tasks/sop` 能转发到 MetaGPT-X；Cloud 中 MetaGPT 不可达时返回 `blocked` 占位 job_id，见 `docs/BLOCKERS.md`。

---

## P1 — MVP

### 1.1 后端
- [x] PostgreSQL schema migration（users, notes, workspace_folders, tasks）
- [x] JWT 鉴权
- [x] 工作区 CRUD + 对话分区导出 JSON/Markdown
- [x] Dify API 代理（创建会话、@引用笔记 ID）
- [x] 笔记 CRUD（document 模板）
- [x] 任务日历 API（对接 tasks 表）

### 1.2 MetaGPT 深度对接
- [x] 任务类型映射：研究型/写作型/检索型 → SOP idea 模板
- [x] 优先级队列：高→MetaGPT 插队标记；中/低→Redis 延迟队列（API 骨架）
- [x] WS 日志转发到 Flutter（MetaGPT 不可达时返回 blocked 事件）
- [x] QA 失败 → `optimize` 端点重试

### 1.3 Flutter
- [x] 五 Tab 导航（广场/工作区/写笔记/好友/个人）壳
- [x] 工作区树形列表
- [x] 新对话页 + 导入 PDF/笔记按钮
- [x] 布置任务页
- [x] 纯文档笔记编辑器

### 1.4 基础设施
- [x] docker compose up：postgres, redis, qdrant, meilisearch（Cloud 无 Docker，配置已验证阻塞）
- [x] Dify 自托管 + 创建「林」Agent（文档 + API 占位）

**P1 完成标准**：用户可聊天、写笔记、提交任务、在工作区看到 MetaGPT 任务状态。

---

## P2 — 社交与工作流

- [x] OpenIM 集成（好友/群聊/团队）
- [x] 广场 Feed + 赞/踩需理由
- [x] React Flow 工作流 WebView
- [x] Dify Agent 插件市场同步
- [x] 搜索（Meilisearch 索引笔记与帖子）
- [x] 个人主页（作品/收藏/标签）

---

## P3 — 知识图谱与 AI 小程序

- [x] Neo4j 笔记关系抽取 pipeline
- [x] sigma.js 图谱 WebView（广场 + DIY 页）
- [x] 好友 AI：按用户笔记分库 RAG（Dify + Qdrant）
- [x] AI 小程序：Dify Workflow + e2b 沙箱
- [x] tldraw 无限画布模板
- [x] 双联 PDF 阅读

---

## P4 — 电商与桌面

- [x] Medusa 对接订单/购物车/钱包
- [x] Tauri 或 Flutter desktop 打包
- [x] 离线缓存（23 篇笔记）
- [x] 性能与压测（接口占位 + 本地验收文档）

---

## 工作流自动续跑（Cursor Hook）

Agent 每完成一步应更新 `.cursor/WORKFLOW_STATE.json`，Hook 在 `stop` 时读取并自动发送下一步指令，无需用户输入「继续」。

当前步骤见 `WORKFLOW_STATE.json` → `current_step`。

---

## 风险与依赖

| 风险 | 缓解 |
|------|------|
| MetaGPT 单 worker 瓶颈 | 重型任务串行；轻量 AI 走 Dify |
| Conda/pip SSL 异常 | 使用独立 venv + 官方 Python 3.11 |
| Dify 部署复杂 | Phase 1 可先用 Dify Cloud 调试 |
| Flutter + WebView 性能 | 图谱/画布按需加载 |

---

## 命令速查

```powershell
# 拉依赖
powershell -File G:\方案分析\zhixing\scripts\clone-deps.ps1

# 启动中间件
cd G:\方案分析\zhixing\infra
docker compose up -d

# 启动 MetaGPT-X（另开终端）
powershell -File G:\MetaGPT\scripts\start_metagpt_x_api.ps1

# 启动知行 API
cd G:\方案分析\zhixing\services\api
python -m uvicorn main:app --reload --port 8080

# Flutter
cd G:\方案分析\zhixing\apps\mobile
flutter run
```
