# 巧侬部署前说明

本目录只提供不含凭据的巧侬独立部署模板。部署动作必须在用户验收公开页面、真实主体资料和迁移内容后执行，不得复用婵泉的应用目录、虚拟环境、数据库角色、数据库、环境变量、媒体、socket、服务或备份。

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

## 部署顺序

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

## 上线前人工确认

- 公司主体、地址、电话、备案号及备案链接。
- 品牌介绍、政策正文、二维码和 Logo 的有效性及版权。
- 50 个迁移产品的名称、分类、功效表述、图片和公开状态。
- 根域名与 `www` 的主域选择和 301 跳转方向。
- 旧 PHP URL 的重定向清单是否需要上线。
- 数据库与媒体备份是否能在不读取婵泉数据的情况下恢复。

## 回滚原则

部署前记录当前提交号并完成数据库与媒体备份。若新版本异常，先恢复上一版代码和前端构建产物；涉及不兼容迁移时使用部署前数据库备份恢复，不在未评估数据影响时直接反向执行迁移。
