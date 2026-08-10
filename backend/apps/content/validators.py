from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


def validate_content_image(image):
    if Path(image.name).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValidationError("仅支持 JPG、PNG 或 WebP 图片。")
    if image.size > 10 * 1024 * 1024:
        raise ValidationError("图片大小不能超过 10 MB。")
    width, height = get_image_dimensions(image)
    if not width or not height:
        raise ValidationError("无法识别图片尺寸。")
    if width > 8000 or height > 8000:
        raise ValidationError("图片宽高均不能超过 8000 像素。")
