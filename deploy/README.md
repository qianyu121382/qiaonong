# 巧侬生产部署说明

本目录保存不含凭据的巧侬独立生产部署配置与固定脚本的仓库来源。第一版已经上线，当前由成功的 `main` push Checks 自动触发精确提交部署。巧侬不得复用婵泉的应用目录、虚拟环境、数据库角色、数据库、环境变量、媒体、socket、服务或备份。

巧侬专用 CD 的完整信任边界、部署流程和安装结果见 `docs/CD方案与接入说明.md`。`qiaonong-cd-dispatch`、`qiaonong-cd-entrypoint` 和 `qiaonong-cd-backup.py` 是服务器固定脚本的仓库来源，不得由普通代码部署直接覆盖 `/usr/local/sbin/` 中的 root-owned 副本。普通业务开发不修改服务器 SSH、sudoers、虚拟环境权限或共享构建锁配置。

CD 与婵泉采用一致的安全原则，但所有脚本、Key、Environment、路径、用户、服务和备份保持独立。两项目唯一共用的是无业务数据的 `/run/lock/company-sites-cd.lock`，并且都必须先获取共享锁、再获取自己的项目锁。

CD 使用三个独立职责：`qiaonong-cd` 只承载 forced-command SSH Key；root-owned 固定入口只负责固定校验、锁、受保护备份、Nginx 与 systemd；不可登录且无 sudo 的 `qiaonong:www-data` 负责 Git、npm、pip、Django 与 Gunicorn。待部署仓库代码不得由维护账号或 root 执行。

## 目标资源

```text
/srv/qiaonong/app
/srv/qiaonong/venv
/srv/qiaonong/media
/srv/qiaonong/static
/srv/qiaonong/logs
/srv/qiaonong/backups
/run/qiaonong/gunicorn.sock
```

## 首次部署顺序（历史基线）

1. 创建独立 Linux 运行用户、目录权限、PostgreSQL 角色和数据库。
2. 拉取已通过 CI 的明确提交，不直接部署未确认的工作区。
3. 创建 `/srv/qiaonong/venv`，安装 `backend/requirements/prod.txt`。
4. 分别在 `frontend/` 与 `admin-frontend/` 执行 `npm ci && npm run build`，线上不常驻 Node.js。
5. 由 `deploy/qiaonong.env.example` 创建权限为 `600` 的 `backend/.env`，填入独立生产凭据。
6. 执行 Django 检查、迁移和静态文件收集：

   ```bash
   DJANGO_SETTINGS_MODULE=config.settings.production /srv/qiaonong/venv/bin/python manage.py check --deploy
   DJANGO_SETTINGS_MODULE=config.settings.production /srv/qiaonong/venv/bin/python manage.py migrate
   DJANGO_SETTINGS_MODULE=config.settings.production /srv/qiaonong/venv/bin/python manage.py collectstatic --noinput
   ```

7. 使用 Django 管理命令创建巧侬独立管理员账号，不复制其他项目账号。
8. 安装并启动 `qiaonong.service`，安装单独的 Nginx 站点配置；执行 `systemctl status`、`journalctl` 与 `nginx -t` 检查。
9. 先用临时域名或本机 Host 映射验收，再修改正式 DNS。
10. 为根域名和 `www` 单独申请证书，确认 HTTPS 后启用安全 Cookie、HTTPS 跳转和 HSTS。
11. 运行 `scripts/check_deployment.py https://zgqnht.com`，人工复核登录、上传、上下架和手机端。
12. 配置巧侬独立数据库与媒体备份，并完成至少一次恢复演练。

## 首次上线前人工确认（已执行）

- 公司主体、地址、电话、备案号及备案链接。
- 品牌介绍、政策正文、二维码和 Logo 的有效性及版权。
- 50 个迁移产品的名称、分类、功效表述、图片和公开状态。
- 根域名与 `www` 的主域选择和 301 跳转方向。
- 旧 PHP URL 的重定向清单是否需要上线。
- 数据库与媒体备份是否能在不读取婵泉数据的情况下恢复。

## 回滚原则

人工部署前记录当前提交号并完成巧侬独立备份。CD 每次版本变更会备份数据库和两个旧前端构建：迁移开始前失败时自动恢复上一版代码、依赖、静态文件、两个 `dist` 和服务；迁移开始后失败时不自动反向迁移，也不盲目恢复旧代码，而是保留部署前快照并转人工评估。媒体的定期备份与恢复继续作为独立运维流程，不与每次 CD 构建混在一起。

仓库中的 CD 文件已完成服务器安装和自动部署验收；服务器 `/usr/local/sbin/` 使用 root-owned 固定副本，普通应用部署不会覆盖。`.github/workflows/`、`deploy/`、CD 方案文档及服务器权限设计当前处于冻结状态，除非用户明确要求或发现阻断安全部署的实际缺陷。
