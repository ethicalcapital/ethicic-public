# Migration to add philosophy fields to HomePage
from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0002_add_missing_homepage_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='philosophy_title',
            field=models.CharField(blank=True, default='Ethics Reveal Quality', max_length=200),
        ),
        migrations.AddField(
            model_name='homepage',
            name='philosophy_content',
            field=wagtail.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='homepage',
            name='philosophy_highlight',
            field=models.CharField(blank=True, default='', help_text='Text to highlight in the philosophy section', max_length=200),
        ),
    ]