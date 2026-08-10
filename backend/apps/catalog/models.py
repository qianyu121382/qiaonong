from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_catalog_image


class Category(models.Model):
    name = models.CharField("名称", max_length=100)
    slug = models.SlugField("页面地址", max_length=120, unique=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="上级分类",
        related_name="children",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    description = models.TextField("简介", blank=True)
    banner = models.ImageField(
        "栏目图",
        upload_to="catalog/categories/%Y/%m/",
        validators=[validate_catalog_image],
        blank=True,
    )
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_active = models.BooleanField("启用", default=True, db_index=True)
    legacy_id = models.PositiveIntegerField(
        "旧站分类 ID", null=True, blank=True, unique=True
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "产品分类"
        verbose_name_plural = "产品分类"

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not self.parent_id:
            return
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({"parent": "分类不能以自身作为上级分类。"})
        if self.parent.parent_id:
            raise ValidationError({"parent": "产品分类最多只能有两级。"})
        if self.pk and self.children.exists():
            raise ValidationError({"parent": "已有下级分类的一级分类不能改为二级分类。"})


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        verbose_name="所属分类",
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField("名称", max_length=160)
    slug = models.SlugField("页面地址", max_length=180, unique=True)
    tag = models.CharField("标签", max_length=80, blank=True)
    summary = models.TextField("摘要", blank=True)
    specification = models.CharField("规格", max_length=200, blank=True)
    description = models.TextField("详情正文", blank=True)
    cover = models.ImageField(
        "封面图",
        upload_to="catalog/products/%Y/%m/",
        validators=[validate_catalog_image],
        blank=True,
    )
    hover_image = models.ImageField(
        "悬停图",
        upload_to="catalog/products/%Y/%m/",
        validators=[validate_catalog_image],
        blank=True,
    )
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_featured = models.BooleanField("首页推荐", default=False, db_index=True)
    is_active = models.BooleanField("上架", default=False, db_index=True)
    legacy_id = models.PositiveIntegerField(
        "旧站产品 ID", null=True, blank=True, unique=True
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "产品"
        verbose_name_plural = "产品"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="产品",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        "图片",
        upload_to="catalog/products/%Y/%m/",
        validators=[validate_catalog_image],
    )
    alt_text = models.CharField("替代文字", max_length=160, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "产品图片"
        verbose_name_plural = "产品图片"

    def __str__(self):
        return f"{self.product.name} - {self.id}"
