from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_content_image


class SiteSettings(models.Model):
    site_name = models.CharField("网站名称", max_length=100, default="巧侬")
    logo = models.ImageField(
        "Logo",
        upload_to="content/site/%Y/%m/",
        validators=[validate_content_image],
        blank=True,
    )
    home_title = models.CharField("首页标题", max_length=160, blank=True)
    home_subtitle = models.TextField("首页副标题", blank=True)
    home_intro_title = models.CharField("首页介绍标题", max_length=160, blank=True)
    home_intro_body = models.TextField("首页介绍正文", blank=True)
    home_intro_image = models.ImageField(
        "首页介绍图片",
        upload_to="content/site/%Y/%m/",
        validators=[validate_content_image],
        blank=True,
    )
    company_name = models.CharField("公司名称", max_length=160, blank=True)
    phone = models.CharField("联系电话", max_length=80, blank=True)
    email = models.EmailField("联系邮箱", blank=True)
    address = models.CharField("联系地址", max_length=255, blank=True)
    social_qr = models.ImageField(
        "社交二维码",
        upload_to="content/site/%Y/%m/",
        validators=[validate_content_image],
        blank=True,
    )
    footer_text = models.CharField("页脚补充文字", max_length=255, blank=True)
    icp_number = models.CharField("ICP备案号", max_length=80, blank=True)
    icp_url = models.URLField(
        "备案链接", default="https://beian.miit.gov.cn/", blank=True
    )
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "网站设置"
        verbose_name_plural = "网站设置"

    def save(self, *args, **kwargs):
        if self.pk not in (None, 1):
            raise ValidationError("网站设置只能保留一份。")
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("网站设置不能删除。")

    def __str__(self):
        return self.site_name


class HeroSlide(models.Model):
    title = models.CharField("标题", max_length=160, blank=True)
    subtitle = models.CharField("副标题", max_length=255, blank=True)
    image = models.ImageField(
        "桌面端图片",
        upload_to="content/slides/%Y/%m/",
        validators=[validate_content_image],
    )
    mobile_image = models.ImageField(
        "手机端图片",
        upload_to="content/slides/%Y/%m/",
        validators=[validate_content_image],
        blank=True,
        help_text="可选；未上传时手机端使用桌面端图片。",
    )
    link_url = models.CharField("链接", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_active = models.BooleanField("启用", default=True, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "首页轮播图"
        verbose_name_plural = "首页轮播图"

    def __str__(self):
        return self.title or f"轮播图 {self.pk}"


class ContentPage(models.Model):
    slug = models.SlugField("页面地址", max_length=120, unique=True)
    title = models.CharField("标题", max_length=160)
    summary = models.TextField("摘要", blank=True)
    body = models.TextField("正文", blank=True)
    image = models.ImageField(
        "页面图片",
        upload_to="content/pages/%Y/%m/",
        validators=[validate_content_image],
        blank=True,
    )
    sort_order = models.PositiveIntegerField("排序", default=0, db_index=True)
    is_active = models.BooleanField("公开", default=False, db_index=True)
    legacy_id = models.PositiveIntegerField(
        "旧站栏目 ID", null=True, blank=True, unique=True
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ("sort_order", "id")
        verbose_name = "内容页面"
        verbose_name_plural = "内容页面"

    def __str__(self):
        return self.title
