# 巧侬网站后端

Django + Django REST Framework 基础工程。当前只包含环境配置和健康检查，不包含产品或页面业务模型。

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
