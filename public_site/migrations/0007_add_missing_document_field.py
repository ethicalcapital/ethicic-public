# Generated manually to add missing requires_request field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0006_add_strategy_related_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategydocument',
            name='requires_request',
            field=models.BooleanField(default=True, help_text='Document requires request'),
        ),
    ]