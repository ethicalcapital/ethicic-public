# Generated manually to fix schema issues
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0002_aboutpage_advisorpage_blogindexpage_blogpost_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutpage',
            name='headshot_image',
            field=models.URLField(blank=True, null=True, default="https://pub-324a685032214395a8bcad478c265d4b.r2.dev/headshot%20sketch_slim.png", help_text="URL to headshot image"),
        ),
        migrations.AlterField(
            model_name='aboutpage',
            name='philosophy_quote_link',
            field=models.URLField(blank=True, null=True, default="/blog/how-i-became-an-active-manager/", help_text="Link for the philosophy quote attribution"),
        ),
    ]
