import json
import re
from pathlib import Path

from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.utils.html import escape, strip_tags
from django.views import View

from apps.catalog.models import Category, Product
from apps.content.models import ContentPage, SiteSettings


SITE_URL = "https://zgqnht.com"


def _site_url():
    return getattr(settings, "PUBLIC_SITE_URL", SITE_URL).rstrip("/")


def _absolute(path):
    return f"{_site_url()}{path}"


def _plain(value, limit=180):
    text = " ".join(strip_tags(value or "").split())
    return text[:limit]


def _image_url(field):
    if not field:
        return ""
    try:
        return _absolute(field.url)
    except ValueError:
        return ""


def _shell():
    dist_root = Path(
        getattr(
            settings,
            "FRONTEND_DIST_ROOT",
            settings.BASE_DIR.parent / "frontend" / "dist",
        )
    )
    index_path = dist_root / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return """<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body><div id=\"app\"></div></body></html>"""


def _render_html(*, title, description, canonical, body, image="", noindex=False, schema=None):
    shell = _shell()
    shell = re.sub(r"\s*<title>.*?</title>", "", shell, flags=re.I | re.S)
    shell = re.sub(
        r"\s*<meta\s+name=[\"']description[\"'][^>]*>", "", shell, flags=re.I
    )
    shell = re.sub(
        r"\s*<link\s+rel=[\"']canonical[\"'][^>]*>", "", shell, flags=re.I
    )
    robots = "noindex,follow" if noindex else "index,follow"
    head = [
        f"<title>{escape(title)}</title>",
        f'<meta name="description" content="{escape(description)}">',
        f'<meta name="robots" content="{robots}">',
        f'<link rel="canonical" href="{escape(canonical)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{escape(title)}">',
        f'<meta property="og:description" content="{escape(description)}">',
        f'<meta property="og:url" content="{escape(canonical)}">',
    ]
    if image:
        head.append(f'<meta property="og:image" content="{escape(image)}">')
    if schema:
        payload = json.dumps(schema, ensure_ascii=False).replace("</", "<\\/")
        head.append(f'<script type="application/ld+json">{payload}</script>')
    shell = shell.replace("</head>", "\n    " + "\n    ".join(head) + "\n  </head>")
    prerender = f'<div id="app"><div class="seo-prerender">{body}</div></div>'
    shell = re.sub(r'<div\s+id=["\']app["\']\s*>.*?</div>', prerender, shell, count=1, flags=re.S)
    return HttpResponse(shell, content_type="text/html; charset=utf-8")


def _organization_schema(site):
    name = site.company_name or site.site_name or "巧侬花田"
    schema = {"@context": "https://schema.org", "@type": "Organization", "name": name, "url": _site_url()}
    if site.company_name:
        schema["legalName"] = site.company_name
    if site.site_name and site.site_name != name:
        schema["alternateName"] = site.site_name
    if site.logo:
        schema["logo"] = _image_url(site.logo)
    if site.phone:
        schema["telephone"] = site.phone
    if site.email:
        schema["email"] = site.email
    if site.address:
        schema["address"] = site.address
    return schema


class HomeSeoView(View):
    def get(self, request):
        site = SiteSettings.objects.first() or SiteSettings()
        categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by("sort_order", "id")
        featured = Product.objects.filter(is_active=True, is_featured=True).order_by("sort_order", "id")[:8]
        links = "".join(f'<li><a href="/products/{escape(item.slug)}">{escape(item.name)}</a></li>' for item in categories)
        products = "".join(f'<li><a href="/product/{escape(item.slug)}">{escape(item.name)}</a></li>' for item in featured)
        intro = _plain(site.home_intro_body, 500)
        body = f"<main><h1>{escape(site.home_title or '巧侬花田')}</h1><p>{escape(site.home_subtitle or intro)}</p><h2>产品系列</h2><ul>{links}</ul><h2>推荐产品</h2><ul>{products}</ul><p><a href=\"/brand\">品牌介绍</a> <a href=\"/contact\">联系我们</a></p></main>"
        description = _plain(site.home_subtitle or site.home_intro_body) or "巧侬花田官方网站，展示品牌介绍、护肤产品、院护系列、医美产品及联系方式。"
        return _render_html(
            title="巧侬花田官网 - 护肤、院护与医美产品",
            description=description,
            canonical=_absolute("/"),
            body=body,
            image=_image_url(site.home_intro_image),
            schema=_organization_schema(site),
        )


class ProductListSeoView(View):
    def get(self, request, slug=None):
        products = Product.objects.filter(is_active=True, category__is_active=True).filter(
            Q(category__parent__isnull=True) | Q(category__parent__is_active=True)
        )
        title = "全部产品"
        description = "浏览巧侬花田已公开的护肤、眼部、水光、彩妆、院护及医美产品资料。"
        image = ""
        if slug:
            try:
                category = Category.objects.get(slug=slug, is_active=True)
            except Category.DoesNotExist as error:
                raise Http404 from error
            title = category.name
            description = _plain(category.description) or f"浏览巧侬花田{category.name}系列及相关产品资料。"
            image = _image_url(category.parent.banner if category.parent_id else category.banner)
            if category.parent_id:
                products = products.filter(category=category)
            else:
                products = products.filter(Q(category=category) | Q(category__parent=category))
        items = "".join(
            f'<li><a href="/product/{escape(item.slug)}">{escape(item.name)}</a><p>{escape(_plain(item.summary))}</p></li>'
            for item in products.order_by("sort_order", "id")
        )
        path = f"/products/{slug}" if slug else "/products"
        body = f'<main><h1>{escape(title)}</h1><p>{escape(description)}</p><ul>{items}</ul></main>'
        return _render_html(
            title=f"{title} - 巧侬花田",
            description=description,
            canonical=_absolute(path),
            body=body,
            image=image,
        )


class ProductDetailSeoView(View):
    def get(self, request, slug):
        try:
            product = Product.objects.select_related("category").get(
                slug=slug,
                is_active=True,
                category__is_active=True,
            )
        except Product.DoesNotExist as error:
            raise Http404 from error
        if product.category.parent_id and not product.category.parent.is_active:
            raise Http404
        description = _plain(product.summary or product.description) or f"巧侬花田{product.name}产品资料。"
        body = (
            f'<main><nav><a href="/products">产品中心</a> / '
            f'<a href="/products/{escape(product.category.slug)}">{escape(product.category.name)}</a></nav>'
            f"<h1>{escape(product.name)}</h1><p>{escape(description)}</p>"
            f"<p>{escape(_plain(product.description, 2000))}</p>"
            f'<p><a href="/contact">联系我们</a></p></main>'
        )
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product.name,
            "description": description,
            "url": _absolute(f"/product/{product.slug}"),
            "brand": {"@type": "Brand", "name": "巧侬花田"},
        }
        image = _image_url(product.cover)
        if image:
            schema["image"] = image
        return _render_html(
            title=f"{product.name} - 巧侬花田",
            description=description,
            canonical=_absolute(f"/product/{product.slug}"),
            body=body,
            image=image,
            schema=schema,
        )


class ContentSeoView(View):
    def get(self, request, slug):
        try:
            page = ContentPage.objects.get(slug=slug, is_active=True)
        except ContentPage.DoesNotExist as error:
            raise Http404 from error
        path = "/brand" if slug == "brand" else "/contact" if slug == "contact" else f"/policy/{slug}"
        description = _plain(page.summary or page.body) or f"巧侬花田{page.title}。"
        body = f'<main><h1>{escape(page.title)}</h1><p>{escape(description)}</p><div>{escape(_plain(page.body, 5000))}</div></main>'
        schema = _organization_schema(SiteSettings.objects.first() or SiteSettings()) if slug in {"brand", "contact"} else None
        return _render_html(
            title=f"{page.title} - 巧侬花田",
            description=description,
            canonical=_absolute(path),
            body=body,
            image=_image_url(page.image),
            schema=schema,
        )


class SearchSeoView(View):
    def get(self, request):
        return _render_html(
            title="站内搜索 - 巧侬花田",
            description="巧侬花田站内产品搜索。",
            canonical=_absolute("/search"),
            body='<main><h1>站内搜索</h1><p><a href="/products">浏览全部产品</a></p></main>',
            noindex=True,
        )


class RobotsView(View):
    def get(self, request):
        content = f"User-agent: *\nAllow: /\nDisallow: /manage/\nDisallow: /api/\nDisallow: /admin/\nSitemap: {_absolute('/sitemap.xml')}\n"
        return HttpResponse(content, content_type="text/plain; charset=utf-8")


class SitemapView(View):
    def get(self, request):
        urls = [(_absolute("/"), None), (_absolute("/products"), None)]
        urls.extend(
            (_absolute(f"/products/{item.slug}"), item.updated_at)
            for item in Category.objects.filter(is_active=True).order_by("id")
        )
        urls.extend(
            (_absolute(f"/product/{item.slug}"), item.updated_at)
            for item in Product.objects.filter(is_active=True, category__is_active=True)
            .filter(Q(category__parent__isnull=True) | Q(category__parent__is_active=True))
            .order_by("id")
        )
        for page in ContentPage.objects.filter(is_active=True).order_by("id"):
            path = "/brand" if page.slug == "brand" else "/contact" if page.slug == "contact" else f"/policy/{page.slug}"
            urls.append((_absolute(path), page.updated_at))
        entries = []
        for location, updated_at in urls:
            lastmod = f"<lastmod>{updated_at.date().isoformat()}</lastmod>" if updated_at else ""
            entries.append(f"<url><loc>{escape(location)}</loc>{lastmod}</url>")
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(entries) + "</urlset>"
        return HttpResponse(xml, content_type="application/xml; charset=utf-8")
