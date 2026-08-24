# 巧侬 CD 方案与接入说明

最后更新：2026-08-24

## 1. 当前状态

巧侬已完成安全 CD 的仓库待安装版本。当前先完成仓库验证和 CI，尚未把本版本固定脚本、传输用户、最小 sudoers、共享锁或 service 模板安装到服务器，也不会在本轮触发生产 CD。

2026-08-24 只读核对的生产现状：

- 线上提交与远端 `main` 均为 `ff59d6ada50f378568186d93728d73923bdd863e`，工作区干净并处于 detached HEAD；
- `qiaonong.service` 已启用且运行正常，使用 `qiaonong:www-data`；
- Gunicorn Socket 为 `/run/qiaonong/gunicorn.sock`；
- 数据库与角色为 `qiaonong_prod`、`qiaonong_app`；
- 官网和管理后台通过本机正式证书加 `--resolve` 检查；
- 两个前端 `dist` 当前目录权限为 `755`、入口文件为 `644`；
- 生产 Node/npm 安装在 `/usr/local/bin`，固定入口已按该真实路径调用，不使用婵泉或本机假定路径；
- 生产 service 文件与改造前仓库模板一致；本轮仓库模板增加 `UMask=0027`、`NoNewPrivileges=true` 和严格文件系统保护，需在统一维护窗口安装。生产 Nginx 已包含 HTTPS 配置，与初始仓库模板不同，CD 只执行 `nginx -t`，不会覆盖它；
- `/srv/qiaonong/venv` 当前属于 `root:root`，正式安装 CD 前需要把这个巧侬独立虚拟环境调整为 `qiaonong:www-data`，使依赖安装不以 root 执行。
- `/srv/qiaonong/backups` 当前仍由旧方式管理；统一安装时必须调整为 `root:root` 且组和其他用户不可写，由 root 固定入口保护部署快照。

只读调查使用巧侬自己的维护身份和现有已信任 Host Key，没有读取或操作婵泉目录、配置或数据。

## 2. 与婵泉对齐但保持隔离

两个项目已确认采用相同的安全流程，但不共用业务资源：

- GitHub 只传完整 SHA；
- 目标属于各自 `origin/main`，且精确提交的 main push CI 已成功；
- 服务器只允许从当前线上提交 fast-forward；
- root 固定入口负责校验、锁、Nginx 和 systemd；
- Git、npm、pip 和 Django 由各自无 sudo、不可登录的项目用户执行；
- 按“同机共享锁 → 项目锁”的顺序覆盖完整部署；
- 部署前备份数据库并保存两个旧 `dist`；
- 迁移开始前失败自动恢复，迁移开始后停止自动回退并转人工评估；
- 本机 HTTPS 使用正式域名、正式证书和 `--resolve`，不使用 `--insecure`；
- 固定脚本通过双端语法检查、SHA-256 核对和 root 原子安装更新。

共享的只有 `/run/lock/company-sites-cd.lock`。巧侬不使用婵泉 Environment、Secrets、Key、入口、项目用户、数据库、媒体、日志或备份。

## 3. 仓库文件与服务器固定副本

| 仓库文件 | 后续服务器固定副本 | 职责 |
| --- | --- | --- |
| `.github/workflows/deploy.yml` | 不安装 | 手动校验并请求部署 |
| `deploy/qiaonong-cd-dispatch` | `/usr/local/sbin/qiaonong-cd-dispatch` | forced command，只接受 `deploy <SHA>` |
| `deploy/qiaonong-cd-entrypoint` | `/usr/local/sbin/qiaonong-cd-entrypoint` | 固定路径、锁、构建、迁移、回滚和检查 |
| `deploy/qiaonong-cd-backup.py` | `/usr/local/sbin/qiaonong-cd-backup` | 低权限读取巧侬 `.env` 并把数据库转储输出给固定入口 |
| `deploy/qiaonong.service` | `/etc/systemd/system/qiaonong.service` | 以 `qiaonong:www-data` 运行并限制服务写入范围 |

服务器固定副本必须属于 root，普通用户不可写。普通 CD 只部署应用提交，绝不自动更新这些高权限固定副本。

## 4. GitHub Actions

创建独立 Environment：

```text
qiaonong-production
```

配置完全独立的 Environment Secrets：

```text
QIAONONG_SSH_HOST
QIAONONG_SSH_USER
QIAONONG_SSH_PRIVATE_KEY
QIAONONG_SSH_KNOWN_HOSTS
```

工作流第一版仅支持 `workflow_dispatch`，并执行：

1. 校验完整、小写的 40 位 SHA；
2. 验证目标提交属于 `origin/main`；
3. 查询 `checks.yml`，要求精确 SHA 存在成功的 main push CI；
4. 通过 `qiaonong-production` 审批和独立并发组；
5. 由 `QIAONONG_SSH_USER=qiaonong-cd` 使用严格 Host Key 校验的巧侬专用 SSH Key 发送 `deploy <SHA>`；
6. 部署后从 Runner 运行公开站检查；
7. 无论成功或失败都删除 Runner 临时 SSH 文件。

GitHub 不保存 Django `.env`、数据库密码、管理员密码、人工维护私钥或婵泉的任何 Secret。

## 5. 服务器固定入口行为

入口只允许操作：

```text
/srv/qiaonong/app
/srv/qiaonong/venv
/srv/qiaonong/media
/srv/qiaonong/static
/srv/qiaonong/logs
/srv/qiaonong/backups
/run/qiaonong/gunicorn.sock
qiaonong.service
```

部署步骤：

1. 验证 root 固定入口、目录、owner、service、origin、无登录项目用户及 `.env` 可读性；
2. 先获取 `/run/lock/company-sites-cd.lock`，再获取 `/run/lock/qiaonong-cd.lock`；
3. 检查包括未跟踪文件在内的生产工作区；
4. 获取远端 `main`，验证目标属于 `origin/main`，且当前线上 SHA 是目标 SHA 的祖先；
5. 要求两个现有 `dist` 安全、完整且不含符号链接或硬链接；
6. root 创建并保护快照目录、完整保存两个旧 `dist`；`qiaonong` 用户只读取自己的 `.env` 并执行 `pg_dump`，root 将输出写入巧侬备份目录；
7. 检出明确目标 SHA；
8. 以 `qiaonong` 用户安装依赖、构建两个前端、执行 Django 命令；
9. 仅对两个公开 `dist` 执行 `chmod -R a+rX`；
10. 执行迁移一致性检查、生产检查、迁移和 collectstatic；
11. root 执行 `nginx -t`，只重启 `qiaonong.service`；
12. 验证 Gunicorn Socket、官网 HTTPS、管理后台 HTTPS 和最终提交 SHA。

本机 HTTPS 固定使用：

```bash
curl --resolve zgqnht.com:443:127.0.0.1 https://zgqnht.com/
curl --resolve zgqnht.com:443:127.0.0.1 https://zgqnht.com/manage/
```

该检查验证服务器当前正式证书，不使用 `--insecure`，也不依赖公网 DNS 回源。

## 6. 权限模型

权限分为三个职责层次：

- `qiaonong-cd`：密码锁定的专用 SSH 传输用户，只承载巧侬 forced-command Key，只能通过精确 sudoers 调用巧侬固定入口；
- root-owned 固定入口：负责参数与固定路径校验、共享锁、项目锁、受保护备份目录、`nginx -t` 和 `qiaonong.service`；
- `qiaonong:www-data`：不可登录且无 sudo，只执行巧侬 Git、npm、pip、Django 和 Gunicorn。

仓库代码不会以 `admin` 或 root 运行。root 固定入口不会 source 或解释项目 `.env`。

`qiaonong` 用户必须保持：

- 主组为 `www-data`；
- Shell 为 `/usr/sbin/nologin`；
- 没有 sudo；
- 能写巧侬代码工作区、虚拟环境、npm 缓存、静态文件和媒体，但不能写部署备份目录；
- 能读取 root 所有、组为 `www-data` 的巧侬生产 `.env`。

统一安装阶段需要至少调整以下巧侬独立资源：

```text
/srv/qiaonong/venv     root:root → qiaonong:www-data
/srv/qiaonong/backups  旧权限 → root:root，模式 0700
```

该变更必须在维护窗口单独复核并执行，不涉及 `/srv/chanquan`。

严格 `umask 027` 继续保护源码和私有文件。只有 `frontend/dist` 与 `admin-frontend/dist` 是公开构建产物，允许补充 `a+rX`；不得放宽 `.env`、媒体、日志或备份权限。

## 7. 备份与失败边界

每次实际版本变更前创建：

```text
/srv/qiaonong/backups/deploy-<UTC时间>-<旧SHA>/
├── database-before-deploy.sql.gz
├── frontend-dist/
└── admin-frontend-dist/
```

快照目录属于 `root:root` 且模式为 `0700`。数据库转储由低权限 `qiaonong` 用户生成，root 只接收输出并压缩写入固定快照路径，再通过 `gzip -t` 验证；root 不读取或解释 `.env`。两个旧 `dist` 缺失或快照失败都会停止部署。

失败处理：

- 迁移开始前：恢复旧提交、两个旧 `dist`、旧依赖和静态文件，重启并检查原服务；
- 迁移开始后：不自动反向迁移，也不盲目恢复旧代码，保留快照并输出位置，转人工评估；
- 日常迁移采用 expand/contract，避免新 schema 立即破坏旧代码兼容性。

媒体的每日备份、部署快照保留周期、自动清理和异机备份是后续独立任务。第一版 CD 不自动删除任何备份。

## 8. 固定脚本安全更新流程

脚本变更不能通过普通 CD 自我更新。每次更新固定副本必须：

1. 在维护电脑执行：

   ```bash
   bash -n deploy/qiaonong-cd-dispatch
   bash -n deploy/qiaonong-cd-entrypoint
   python -m py_compile deploy/qiaonong-cd-backup.py
   ```

2. 同时检查待安装 `qiaonong.service`，计算固定脚本和 service 模板的本地 SHA-256 并记录；
3. 使用人工维护连接上传到巧侬专用、不可被其他项目写入的临时位置；
4. 在服务器临时文件上再次执行 Bash/Python 语法检查；
5. 在服务器计算 SHA-256，与维护电脑逐项一致后才继续；
6. 使用 root 权限先安装为目标目录内的 root-owned 临时文件，再通过同文件系统重命名原子替换固定副本；
7. 核对固定副本为 `root:root`、模式 `755`，普通用户不可写；
8. 删除临时上传文件；
9. 重新测试合法 SHA、非法 SHA、Shell、SCP/SFTP、端口转发和跨项目调用均符合预期。

实际安装命令、sudoers 和 `authorized_keys` 内容需要在两项目脚本都通过 CI 后，于统一维护窗口根据服务器实时状态生成。本阶段不提前修改这些共享安全配置。

## 9. 启用前剩余步骤

1. 提交并推送巧侬仓库版本，等待全部 Checks 通过；
2. 与婵泉分别冻结待安装脚本版本并记录提交与 SHA-256；
3. 统一维护窗口调整各自项目用户和目录权限；
4. 安装两项目独立固定入口和最小 sudoers；
5. 安装两把独立 forced-command 公钥；
6. 完成拒绝行为、当前 SHA 幂等检查和共享锁并发测试；
7. 创建 `qiaonong-production` 及巧侬独立 Secrets；
8. 单独执行一次巧侬真实 CD，并核对 SHA、备份、权限、服务、Socket 和 HTTPS。

统一维护窗口还需创建密码锁定、不可承载普通 Shell 的 `qiaonong-cd` 传输用户；为它安装仅调用 `/usr/local/sbin/qiaonong-cd-dispatch` 的 forced-command 公钥和最小 sudoers；安装并核对 root-owned 固定脚本；调整巧侬虚拟环境与备份目录权限；安装强化后的 `qiaonong.service` 并执行 `daemon-reload`；最后完成合法 SHA、非法 SHA、Shell、SCP/SFTP、端口转发、跨项目调用、幂等健康检查及共享锁并发测试。整个过程不得读取或修改婵泉资源。

## 10. CI/CD 冻结范围

本轮提交通过巧侬 `main` push Checks 后，以下内容作为统一维护窗口的冻结版本：

- `.github/workflows/`；
- `deploy/`；
- 本文及服务器权限设计。

后续普通业务开发不得修改这些内容。只有用户明确要求，或验证发现会阻断安全部署的实际缺陷时，才重新解冻并走完整审核、测试和 CI。
