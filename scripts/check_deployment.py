#!/usr/bin/env python3
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def fetch(base_url, path, accept="text/html"):
    request = Request(urljoin(base_url.rstrip("/") + "/", path.lstrip("/")))
    request.add_header("Accept", accept)
    with urlopen(request, timeout=10) as response:
        return response.status, response.headers, response.read()


def main():
    if len(sys.argv) != 2 or not sys.argv[1].startswith(("http://", "https://")):
        raise SystemExit("用法：python scripts/check_deployment.py https://example.com")

    base_url = sys.argv[1]
    checks = (
        ("公开首页", "/", "text/html"),
        ("管理入口", "/manage/", "text/html"),
        ("健康检查", "/api/health/", "application/json"),
        ("公开分类", "/api/catalog/categories/", "application/json"),
        ("网站设置", "/api/content/site/", "application/json"),
    )
    failed = False
    for label, path, accept in checks:
        try:
            status, headers, body = fetch(base_url, path, accept)
            if accept == "application/json":
                json.loads(body)
            print(f"PASS {label}: {status} ({headers.get('content-type', '')})")
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            failed = True
            print(f"FAIL {label}: {error}", file=sys.stderr)

    if base_url.startswith("https://"):
        try:
            _, headers, _ = fetch(base_url, "/")
            print(f"INFO HSTS: {headers.get('strict-transport-security', '未返回')}")
        except (HTTPError, URLError, TimeoutError):
            pass

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
