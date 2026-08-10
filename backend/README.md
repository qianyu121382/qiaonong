# 巧侬网站后端

Django + Django REST Framework 后端，包含管理员 Session/CSRF 认证、网站内容、产品目录、公开 API、管理 API 和旧站产品迁移命令。

## 本地初始化

标准基线需要 Python 3.12、uv 和 PostgreSQL 16。先创建巧侬独立的本地数据库和角色，再执行：

```bash
cd backend
uv venv --python 3.12
uv pip install --python .venv/bin/python -r requirements/dev.lock.txt
cp .env.example .env
.venv/bin/python manage.py migrate
```

不得使用婵泉的数据库、数据库角色、环境变量或媒体目录。

当前 Windows 开发电脑也允许使用已经安装的 `chanquan-django` Conda 环境作为 Python 运行工具。该环境为 Python 3.13，已安装的 Django、DRF、psycopg 和 Pillow 版本与巧侬锁文件一致：

```powershell
conda activate chanquan-django
cd E:\MyCode\Code\qiaonong\backend
python manage.py check
python manage.py runserver
```

共用本地解释器环境不代表共用项目运行环境；巧侬仍必须使用自己的 `.env`、PostgreSQL 数据库与角色、媒体目录和数据。

## 运行与验证

```bash
.venv/bin/python manage.py runserver
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/python manage.py test
```

健康检查地址：`http://127.0.0.1:8000/api/health/`。

## 管理员账号

巧侬管理员必须独立创建，不得复用其他项目账号：

```bash
python manage.py createsuperuser
```

交付给管理员的界面位于 `/manage/`，Django 自带管理界面只作为开发和紧急维护入口。

## 旧站产品迁移

默认把旧站公开归档中的产品导入为下架草稿：

```bash
python manage.py import_legacy_catalog --copy-images
```

命令可重复执行，并用旧站 ID 更新已经导入的数据。不要在内容未经人工核验时使用 `--publish-products`。公司主体、备案、联系信息和政策正文不会自动从旧站迁入。

确认需要制作本地完整预览后，可显式导入旧站公开页面中可确认属于巧侬的 Logo、首页横幅、系列图片、品牌短文和客服电话：

```bash
python manage.py import_legacy_catalog --copy-images --publish-products --import-public-site
```

`--import-public-site` 不导入旧站页脚中的婵泉公司名、地址、备案号，也不填充原本为空的政策正文；已有后台内容优先，不会在重复执行时覆盖管理员后来填写的正文、图片或发布状态。
