from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_DIMENSION = 8000
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def validate_catalog_image(image):
    extension = Path(image.name).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("仅支持 JPG、PNG 或 WebP 图片。")

    if image.size > MAX_IMAGE_BYTES:
        raise ValidationError("图片大小不能超过 10 MB。")

    width, height = get_image_dimensions(image)
    if not width or not height:
        raise ValidationError("无法识别图片尺寸。")
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise ValidationError("图片宽高均不能超过 8000 像素。")
