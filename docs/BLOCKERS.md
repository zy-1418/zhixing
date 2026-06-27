# 知行 Cloud Agent 阻塞项

## Cloud 环境不可用依赖

- Docker：当前镜像缺少 `docker` 命令，无法执行 `infra/docker-compose.yml` 的本机启动验证；已保留 compose 配置，需在本机或 CI Docker 环境复验。
- Flutter SDK：当前镜像缺少 `flutter` 命令，移动端以手写 Flutter 五 Tab 壳与占位页面交付；需在本机 Flutter stable 环境运行 `flutter analyze` / `flutter run`。
- MetaGPT-X：Cloud 环境无法访问宿主机 `127.0.0.1:8000`，`POST /api/v1/tasks/sop` 的真实转发联调需在本机启动 MetaGPT-X 后复验。

## 处理策略

上述阻塞项按自动化规则以占位实现或文档记录方式标记完成，后续步骤继续推进。
