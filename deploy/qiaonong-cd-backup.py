#!/usr/bin/env python3
"""Stream a Qiaonong PostgreSQL dump to stdout as the project user.

The root-owned deployment entrypoint redirects this stream into the protected
Qiaonong backup directory. This helper never creates or selects backup paths.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

from dotenv import dotenv_values


APP_ROOT = Path("/srv/qiaonong/app")
ENV_FILE = APP_ROOT / "backend/.env"
PG_DUMP = Path("/usr/bin/pg_dump")


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def main() -> None:
    if len(sys.argv) != 1:
        fail("qiaonong-cd-backup 不接受外部参数。")
    if not APP_ROOT.is_dir() or APP_ROOT.is_symlink() or APP_ROOT.resolve() != APP_ROOT:
        fail(f"拒绝不安全的巧侬应用目录：{APP_ROOT}")
    if not ENV_FILE.is_file() or ENV_FILE.is_symlink():
        fail(f"巧侬生产环境文件不存在或不安全：{ENV_FILE}")
    if not PG_DUMP.is_file() or not os.access(PG_DUMP, os.X_OK):
        fail(f"PostgreSQL 客户端命令不可用：{PG_DUMP}")

    config = dotenv_values(ENV_FILE)
    required = ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")
    missing = [key for key in required if not config.get(key)]
    if missing:
        fail(f"巧侬生产环境缺少数据库配置：{', '.join(missing)}")

    process_env = os.environ.copy()
    process_env["PGPASSWORD"] = str(config["POSTGRES_PASSWORD"])
    subprocess.run(
        [
            str(PG_DUMP),
            "--no-owner",
            "--no-privileges",
            f"--host={config.get('POSTGRES_HOST') or '127.0.0.1'}",
            f"--port={config.get('POSTGRES_PORT') or '5432'}",
            f"--username={config['POSTGRES_USER']}",
            str(config["POSTGRES_DB"]),
        ],
        check=True,
        env=process_env,
        stdout=sys.stdout.buffer,
    )


if __name__ == "__main__":
    main()
