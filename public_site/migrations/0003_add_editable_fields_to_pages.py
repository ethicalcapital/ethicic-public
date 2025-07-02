# Generated manually to add missing fields for CriteriaPage and SolutionsPage

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('public_site', '0002_initial'),
    ]

    operations = [
        # Create ExclusionCategory model for CriteriaPage
        migrations.CreateModel(
            name='ExclusionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('icon', models.CharField(default='🚫', help_text='Emoji icon for category', max_length=10)),
                ('title', models.CharField(help_text='Category title', max_length=100)),
                ('description', models.TextField(help_text='Description of what is excluded in this category')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='exclusion_categories', to='public_site.criteriapage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        
        # Create StrategyCard model for SolutionsPage
        migrations.CreateModel(
            name='StrategyCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('icon', models.CharField(default='🚀', help_text='Emoji icon for strategy', max_length=10)),
                ('title', models.CharField(help_text='Strategy title', max_length=100)),
                ('description', models.TextField(help_text='Brief description of the strategy')),
                ('features', models.TextField(help_text='Strategy features, one per line')),
                ('url', models.CharField(help_text='URL to strategy page', max_length=200)),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='strategy_cards', to='public_site.solutionspage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        
        # Add additional fields to SolutionsPage
        migrations.AddField(
            model_name='solutionspage',
            name='strategies_section_title',
            field=models.CharField(blank=True, default='Three Strategies, Infinite Possibilities', help_text='Title for strategies section', max_length=200),
        ),
        migrations.AddField(
            model_name='solutionspage',
            name='strategies_intro',
            field=models.TextField(blank=True, default='Our investment solutions are built around three core strategies, tailored to three distinct audiences, and delivered through multiple channels to meet you where you are.', help_text='Introduction text for strategies section'),
        ),
        
        # Add fields to CriteriaPage for additional content
        migrations.AddField(
            model_name='criteriapage',
            name='transparency_section_title',
            field=models.CharField(blank=True, default='Open Source Transparency', help_text='Title for transparency section', max_length=200),
        ),
        migrations.AddField(
            model_name='criteriapage',
            name='transparency_description',
            field=wagtail.fields.RichTextField(blank=True, default='<p>Our ethical screening criteria are publicly available on GitHub. This ensures complete transparency about what we exclude and why.</p>', help_text='Description of transparency approach'),
        ),
        migrations.AddField(
            model_name='criteriapage',
            name='transparency_benefits',
            field=models.TextField(blank=True, default='Full documentation of exclusion criteria\nRegular updates as our research evolves\nCommunity feedback and discussion\nVersion history and change tracking', help_text='Benefits of transparency, one per line'),
        ),
        migrations.AddField(
            model_name='criteriapage',
            name='exclusions_section_title',
            field=models.CharField(blank=True, default='Key Exclusion Categories', help_text='Title for exclusions section', max_length=200),
        ),
        migrations.AddField(
            model_name='criteriapage',
            name='exclusions_note',
            field=wagtail.fields.RichTextField(blank=True, default='<p><strong>Important:</strong> This is a high-level overview. The complete criteria, methodology, and specific examples are detailed in our GitHub repository.</p>', help_text='Note about exclusions'),
        ),
    ]