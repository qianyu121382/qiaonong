#!/usr/bin/env python3
"""Read-only capture of the public zgqnht.com pages and their static assets."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, urlopen


BASE_URL = "http://www.zgqnht.com/"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "migration" / "legacy-site"
USER_AGENT = "Mozilla/5.0 (compatible; QiaonongMigrationCapture/1.0; read-only)"
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\()?\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)


def canonical_page_url(raw_url: str, base_url: str) -> str | None:
    url = urljoin(base_url, unescape(raw_url)).split("#", 1)[0]
    parsed = urlparse(url)
    if parsed.hostname not in {"zgqnht.com", "www.zgqnht.com"}:
        return None
    if parsed.path in {"", "/"}:
        return BASE_URL
    if parsed.path != "/index.php":
        return None
    query = parse_qs(parsed.query)
    route = query.get("s", [""])[0]
    item_id = query.get("id", [""])[0]
    if route not in {"index/category/index", "index/show/index"} or not item_id.isdigit():
        return None
    return f"{BASE_URL}index.php?s={route}&id={int(item_id)}"


def page_filename(url: str) -> str:
    if url == BASE_URL:
        return "home.html"
    query = parse_qs(urlparse(url).query)
    route = query["s"][0]
    item_id = query["id"][0]
    prefix = "category" if route == "index/category/index" else "product"
    return f"{prefix}-{item_id}.html"


def asset_url(raw_url: str, base_url: str) -> str | None:
    raw_url = unescape(raw_url.strip())
    if not raw_url or raw_url.startswith(("data:", "javascript:", "mailto:", "tel:", "#")):
        return None
    url = urljoin(base_url, raw_url).split("#", 1)[0]
    parsed = urlparse(url)
    if parsed.hostname not in {"zgqnht.com", "www.zgqnht.com"}:
        return None
    if parsed.path in {"", "/", "/index.php"}:
        return None
    return f"http://www.zgqnht.com{parsed.path}" + (f"?{parsed.query}" if parsed.query else "")


def decode_body(body: bytes, content_type: str) -> str:
    charset_match = re.search(r"charset=([\w-]+)", content_type, re.IGNORECASE)
    encodings = [charset_match.group(1)] if charset_match else []
    encodings.extend(["utf-8", "gb18030"])
    for encoding in encodings:
        try:
            return body.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", errors="replace")


def fetch(url: str, attempts: int = 3) -> tuple[bytes, str, int]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
            with urlopen(request, timeout=25) as response:
                return response.read(), response.headers.get("Content-Type", ""), response.status
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


class PageParser(HTMLParser):
    RESOURCE_ATTRIBUTES = {
        "img": {"src", "data-src", "data-original"},
        "script": {"src"},
        "link": {"href"},
        "source": {"src", "srcset"},
        "video": {"src", "poster"},
        "audio": {"src"},
        "input": {"src"},
    }
    BLOCK_TAGS = {
        "address", "article", "aside", "blockquote", "br", "div", "footer", "h1", "h2",
        "h3", "h4", "h5", "h6", "header", "li", "main", "nav", "p", "section", "tr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: set[str] = set()
        self.resources: set[str] = set()
        self.text_parts: list[str] = []
        self.title_parts: list[str] = []
        self._ignored_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value for key, value in attrs if value is not None}
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "a" and "href" in attrs_dict:
            self.links.add(attrs_dict["href"])
        for attribute in self.RESOURCE_ATTRIBUTES.get(tag, set()):
            value = attrs_dict.get(attribute)
            if not value:
                continue
            if attribute == "srcset":
                self.resources.update(part.strip().split()[0] for part in value.split(",") if part.strip())
            else:
                self.resources.add(value)
        style = attrs_dict.get("style", "")
        self.resources.update(match[1] for match in CSS_URL_RE.findall(style))
        if tag in self.BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in self.BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        if not self._ignored_depth:
            cleaned = re.sub(r"\s+", " ", data).strip()
            if cleaned:
                self.text_parts.append(cleaned)

    @property
    def title(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.title_parts)).strip()

    @property
    def visible_text(self) -> str:
        text = " ".join(self.text_parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip() + "\n"


def safe_asset_path(url: str, content_type: str) -> Path:
    parsed = urlparse(url)
    relative = parsed.path.lstrip("/") or "asset"
    path = OUTPUT_DIR / "assets" / relative
    if path.suffix == "":
        extension = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ""
        path = path.with_suffix(extension)
    if parsed.query:
        digest = hashlib.sha256(parsed.query.encode()).hexdigest()[:10]
        path = path.with_name(f"{path.stem}-{digest}{path.suffix}")
    return path


def download_asset(url: str) -> tuple[dict[str, object] | None, list[str], dict[str, str] | None]:
    try:
        body, content_type, status = fetch(url, attempts=2)
        path = safe_asset_path(url, content_type)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        record = {
            "url": url,
            "file": str(path.relative_to(OUTPUT_DIR)),
            "status": status,
            "content_type": content_type,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
        }
        references: list[str] = []
        if "text/css" in content_type or path.suffix.lower() == ".css":
            css = decode_body(body, content_type)
            references.extend(match[1] for match in CSS_URL_RE.findall(css))
            references.extend(CSS_IMPORT_RE.findall(css))
        return record, references, None
    except Exception as exc:  # noqa: BLE001
        return None, [], {"type": "asset", "url": url, "error": repr(exc)}


def main() -> None:
    pages_dir = OUTPUT_DIR / "pages"
    text_dir = OUTPUT_DIR / "text"
    pages_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    page_queue: deque[str] = deque([BASE_URL])
    visited_pages: set[str] = set()
    pending_assets: deque[str] = deque()
    known_assets: set[str] = set()
    page_records: list[dict[str, object]] = []
    asset_records: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []

    while page_queue:
        url = page_queue.popleft()
        if url in visited_pages:
            continue
        visited_pages.add(url)
        try:
            body, content_type, status = fetch(url)
            html = decode_body(body, content_type)
            parser = PageParser()
            parser.feed(html)
            filename = page_filename(url)
            (pages_dir / filename).write_text(html, encoding="utf-8")
            (text_dir / filename.replace(".html", ".txt")).write_text(parser.visible_text, encoding="utf-8")

            discovered_pages = {
                normalized
                for link in parser.links
                if (normalized := canonical_page_url(link, url)) is not None
            }
            for discovered in sorted(discovered_pages):
                if discovered not in visited_pages:
                    page_queue.append(discovered)

            discovered_assets = {
                normalized
                for resource in parser.resources
                if (normalized := asset_url(resource, url)) is not None
            }
            for discovered in sorted(discovered_assets):
                if discovered not in known_assets:
                    known_assets.add(discovered)
                    pending_assets.append(discovered)

            page_records.append({
                "url": url,
                "file": f"pages/{filename}",
                "text_file": f"text/{filename.replace('.html', '.txt')}",
                "title": parser.title,
                "status": status,
                "bytes": len(body),
                "links_found": len(discovered_pages),
                "assets_found": len(discovered_assets),
            })
            print(f"PAGE  {status} {url}")
        except Exception as exc:  # noqa: BLE001 - capture should continue and report all failures
            errors.append({"type": "page", "url": url, "error": repr(exc)})
            print(f"ERROR page {url}: {exc}")

    downloaded_assets: set[str] = set()
    with ThreadPoolExecutor(max_workers=6) as executor:
        while pending_assets:
            batch: list[str] = []
            while pending_assets and len(batch) < 24:
                url = pending_assets.popleft()
                if url not in downloaded_assets:
                    downloaded_assets.add(url)
                    batch.append(url)
            futures = {executor.submit(download_asset, url): url for url in batch}
            for future in as_completed(futures):
                url = futures[future]
                record, references, error = future.result()
                if error:
                    errors.append(error)
                    print(f"ERROR asset {url}: {error['error']}")
                    continue
                assert record is not None
                asset_records.append(record)
                print(f"ASSET {record['status']} {record['bytes']:>9} {url}")
                for reference in references:
                    normalized = asset_url(reference, url)
                    if normalized and normalized not in known_assets:
                        known_assets.add(normalized)
                        pending_assets.append(normalized)

    hashes: dict[str, list[str]] = {}
    for record in asset_records:
        hashes.setdefault(str(record["sha256"]), []).append(str(record["file"]))
    duplicate_groups = [files for files in hashes.values() if len(files) > 1]

    manifest = {
        "source": BASE_URL,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "pages": sorted(page_records, key=lambda item: str(item["url"])),
        "assets": sorted(asset_records, key=lambda item: str(item["url"])),
        "errors": errors,
        "summary": {
            "pages": len(page_records),
            "assets": len(asset_records),
            "asset_bytes": sum(int(record["bytes"]) for record in asset_records),
            "errors": len(errors),
            "duplicate_asset_groups": len(duplicate_groups),
        },
        "duplicate_asset_groups": duplicate_groups,
    }
    (OUTPUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
