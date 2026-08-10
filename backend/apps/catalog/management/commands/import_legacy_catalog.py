import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import Category, Product, ProductImage
from apps.content.models import ContentPage


ROOT_CATEGORIES = (
    ("skin-care", "护肤"),
    ("eye-care", "眼部系列"),
    ("aqua-care", "水光系列"),
    ("makeup", "彩妆"),
    ("salon-care", "院护系列"),
    ("medical-beauty", "医美产品"),
)

CHILD_CATEGORIES = (
    (8, "hydrating", "透明质酸钠保湿系列", "skin-care"),
    (9, "butylresorcinol", "4-丁基间苯二酚系列", "skin-care"),
    (10, "proxylane", "玻色因抗衰系列", "skin-care"),
    (11, "collagen-repair", "三型重组胶原蛋白修护系列", "skin-care"),
    (12, "facial-masks", "面膜系列", "skin-care"),
    (13, "special-products", "特色单品", "skin-care"),
    (14, "eye-cream", "玻色因抗皱紧致眼霜", "eye-care"),
    (15, "eye-mask", "玻色因抗皱紧致眼贴膜", "eye-care"),
    (16, "eye-serum", "玻色因抗皱紧致眼部精华液", "eye-care"),
    (17, "hyaluronic-aqua", "透明质酸钠水光精华液", "aqua-care"),
    (18, "salmon-aqua", "三文鱼水光精华液", "aqua-care"),
    (19, "niacinamide-aqua", "烟酰胺水光精华液", "aqua-care"),
    (20, "cushion", "持妆无瑕气垫BB霜", "makeup"),
    (21, "foundation", "柔光持妆粉底液", "makeup"),
    (None, "salon-sets", "套盒", "salon-care"),
    (None, "salon-singles", "单品", "salon-care"),
)

CATEGORY_PAGE_MAP = {
    **{legacy_id: slug for legacy_id, slug, _, _ in CHILD_CATEGORIES if legacy_id},
    **{legacy_id: "salon-sets" for legacy_id in range(24, 27)},
    **{legacy_id: "salon-singles" for legacy_id in range(27, 36)},
    60: "medical-beauty",
}

CONTENT_PAGES = (
    (1, "brand", "品牌介绍"),
    (41, "contact", "联系我们"),
    (43, "usage-policy", "使用政策"),
    (44, "privacy-policy", "隐私条款"),
    (45, "cookies-policy", "Cookies 政策"),
)


def plain_text(fragment):
    fragment = re.sub(r"<\s*br\s*/?\s*>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"</\s*(p|div|li|h[1-6])\s*>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    fragment = html.unescape(fragment).replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in fragment.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def first_match(source, pattern):
    match = re.search(pattern, source, flags=re.I | re.S)
    return match.group(1) if match else ""


class Command(BaseCommand):
    help = "从仓库内只读归档导入旧站产品草稿，默认不上架。"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=Path,
            help="旧站归档目录，默认使用仓库 migration/legacy-site。",
        )
        parser.add_argument(
            "--copy-images",
            action="store_true",
            help="把归档产品图片复制到巧侬 MEDIA_ROOT。",
        )
        parser.add_argument(
            "--publish-products",
            action="store_true",
            help="导入后直接上架；仅应在内容已人工核验时使用。",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        backend_dir = Path(__file__).resolve().parents[4]
        source = (options["source"] or backend_dir.parent / "migration" / "legacy-site").resolve()
        manifest_path = source / "manifest.json"
        if not manifest_path.is_file():
            raise CommandError(f"找不到迁移清单：{manifest_path}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        asset_map = {
            urlsplit(item["url"]).path: source / item["file"]
            for item in manifest["assets"]
            if item.get("status") == 200
        }
        categories = self.create_categories(source, options["copy_images"], asset_map)
        for legacy_id, slug, title in CONTENT_PAGES:
            ContentPage.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "legacy_id": legacy_id,
                    "is_active": False,
                },
            )
        memberships = self.product_memberships(source)

        imported = 0
        missing_category = []
        for page in sorted((source / "pages").glob("product-*.html")):
            legacy_id = int(page.stem.split("-")[1])
            category_slug = memberships.get(legacy_id)
            if not category_slug:
                missing_category.append(legacy_id)
                continue
            product_html = page.read_text(encoding="utf-8")
            name = plain_text(first_match(product_html, r'<div class="ptag">(.*?)</div>'))
            if not name:
                self.stderr.write(f"跳过产品 {legacy_id}：未找到名称")
                continue

            intro = plain_text(first_match(product_html, r'<div class="pintro">(.*?)</div>'))
            detail_parts = []
            detail_block = first_match(
                product_html, r'<div class="product_conbox">(.*?)<div class="footbox">'
            )
            for title, body in re.findall(
                r'<div class="ptnav">.*?<span>(.*?)</span>.*?<div class="pdcon">(.*?)</div>',
                detail_block,
                flags=re.I | re.S,
            ):
                clean_title, clean_body = plain_text(title), plain_text(body)
                if clean_title or clean_body:
                    detail_parts.append(f"{clean_title}\n{clean_body}".strip())
            description = "\n\n".join(part for part in [intro, *detail_parts] if part)

            product, _ = Product.objects.update_or_create(
                legacy_id=legacy_id,
                defaults={
                    "category": categories[category_slug],
                    "name": name,
                    "slug": f"product-{legacy_id}",
                    "summary": intro[:500],
                    "description": description,
                    "sort_order": legacy_id,
                    "is_active": options["publish_products"],
                },
            )
            if options["copy_images"]:
                self.copy_product_images(product, product_html, asset_map)
            imported += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"已导入或更新 {len(categories)} 个分类、{imported} 个产品和 "
                f"{len(CONTENT_PAGES)} 个待核验内容页；"
                f"产品状态：{'已上架' if options['publish_products'] else '草稿/下架'}。"
            )
        )
        if missing_category:
            self.stdout.write(
                self.style.WARNING(
                    "以下旧站产品未能确定分类，未导入："
                    + ", ".join(map(str, missing_category))
                )
            )

    def create_categories(self, source, copy_images, asset_map):
        result = {}
        for order, (slug, name) in enumerate(ROOT_CATEGORIES, start=1):
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "sort_order": order, "is_active": True},
            )
            result[slug] = category

        for order, (legacy_id, slug, name, parent_slug) in enumerate(
            CHILD_CATEGORIES, start=1
        ):
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "parent": result[parent_slug],
                    "sort_order": order,
                    "is_active": True,
                    "legacy_id": legacy_id,
                },
            )
            result[slug] = category

        medical = result["medical-beauty"]
        medical.legacy_id = 60
        medical.save(update_fields=["legacy_id"])

        if copy_images:
            for legacy_id, slug in CATEGORY_PAGE_MAP.items():
                category = result[slug]
                if category.banner:
                    continue
                page = source / "pages" / f"category-{legacy_id}.html"
                if not page.exists():
                    continue
                path = first_match(
                    page.read_text(encoding="utf-8"),
                    r'product_banbox[^>]+background\s*:\s*url\(([^)]+)\)',
                ).strip("'\"")
                source_image = asset_map.get(path)
                if source_image and source_image.is_file():
                    with source_image.open("rb") as image_file:
                        category.banner.save(source_image.name, File(image_file), save=True)
        return result

    def product_memberships(self, source):
        memberships = {}
        for legacy_category_id, category_slug in CATEGORY_PAGE_MAP.items():
            page = source / "pages" / f"category-{legacy_category_id}.html"
            if not page.exists():
                continue
            source_html = page.read_text(encoding="utf-8")
            product_list = source_html.split('class="prolist"', 1)[-1]
            product_list = product_list.split('class="footbox"', 1)[0]
            for product_id in re.findall(r'show/index(?:&amp;|&)id=(\d+)', product_list):
                memberships.setdefault(int(product_id), category_slug)
        return memberships

    def copy_product_images(self, product, source_html, asset_map):
        detail = first_match(source_html, r'<div class="product_detailbox.*?>(.*?)<div class="rconbox">')
        paths = list(dict.fromkeys(re.findall(r'<img[^>]+src="([^"]+)"', detail, flags=re.I)))
        for index, path in enumerate(paths):
            source_image = asset_map.get(path)
            if not source_image or not source_image.is_file():
                continue
            if index == 0 and not product.cover:
                with source_image.open("rb") as image_file:
                    product.cover.save(source_image.name, File(image_file), save=True)
                continue
            if ProductImage.objects.filter(product=product, alt_text=f"旧站图片 {index + 1}").exists():
                continue
            with source_image.open("rb") as image_file:
                image = ProductImage(
                    product=product,
                    alt_text=f"旧站图片 {index + 1}",
                    sort_order=index,
                )
                image.image.save(source_image.name, File(image_file), save=True)
