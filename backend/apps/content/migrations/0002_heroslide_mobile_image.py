import apps.content.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="heroslide",
            name="image",
            field=models.ImageField(
                upload_to="content/slides/%Y/%m/",
                validators=[apps.content.validators.validate_content_image],
                verbose_name="桌面端图片",
            ),
        ),
        migrations.AddField(
            model_name="heroslide",
            name="mobile_image",
            field=models.ImageField(
                blank=True,
                help_text="可选；未上传时手机端使用桌面端图片。",
                upload_to="content/slides/%Y/%m/",
                validators=[apps.content.validators.validate_content_image],
                verbose_name="手机端图片",
            ),
        ),
    ]
