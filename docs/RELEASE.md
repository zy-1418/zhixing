# 知行实施 Release

## 状态

- `WORKFLOW_STATE.json` 已全部 `completed`
- `auto_continue=false`
- P0-P4 计划项已在 `docs/PLAN.md` 勾选

## 主要交付

### 后端

- FastAPI 挂载认证、任务、工作区、笔记、Dify、社交与后续阶段占位路由。
- 注册/登录/JWT 鉴权：`/api/v1/auth/register`、`/api/v1/auth/login`、`/api/v1/auth/me`。
- 工作区树形聚合与对话导出：`/api/v1/workspace/tree`、`/api/v1/workspace/conversations/{id}/export`。
- 笔记 document 默认块与 Markdown/JSON 导出。
- SOP 任务提交、任务日历、MetaGPT 日志 WS、QA retry。
- Dify 代理占位与「林」Agent 状态。
- P2-P4：广场、辩论、市场、搜索、个人主页、图谱、好友 AI、小程序、电商、桌面、离线缓存占位 API。

### 移动端

- Flutter 五 Tab 壳：广场、工作区、写笔记、好友、个人。
- 工作区页包含文件树、新对话、导入 PDF/@笔记、布置任务和工作流入口。
- 写笔记页提供纯文档编辑器壳。
- 广场/好友/个人页提供后续阶段入口。

### WebView/脚本

- React Flow 工作流占位页：`apps/web/workflow/index.html`
- sigma 图谱占位页：`apps/web/graph/index.html`
- tldraw 画布占位页：`apps/web/canvas/index.html`
- pdf.js 双联阅读占位页：`apps/web/pdf_dual/index.html`
- 桌面构建占位脚本：`scripts/build-desktop.ps1`

## Cloud 阻塞

详见 `docs/BLOCKERS.md`。当前环境缺少 Docker、Flutter SDK，且无法访问本机 MetaGPT-X，因此相关能力以可运行占位接口和文档交付。

## 本地验收建议

```powershell
cd infra
docker compose config
docker compose up -d

cd ..\services\api
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn main:app --reload --port 8080

cd ..\..\apps\mobile
flutter run
```
