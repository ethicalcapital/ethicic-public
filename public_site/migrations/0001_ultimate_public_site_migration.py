# ULTIMATE PUBLIC SITE MIGRATION
# Final comprehensive migration consolidating ALL public site migrations
# Originally 33+ individual migrations across 2 files, now unified into ONE
# Covers: Wagtail pages, blog system, encyclopedia, support, advisor pages

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.blocks
import wagtail.contrib.routable_page.models
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    # Note: The replaces directive has been removed to avoid Django migration state
    # reconstruction issues. The individual migrations listed below were previously
    # applied and are now consolidated into this single migration for cleaner history.
    # Original replaced migrations:
    # 0001_initial through 0036_add_blogpost_updated_at_field + 0004_add_featured_field_to_mediaitem

    initial = True

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('wagtailcore', '0094_alter_page_locale'),
        ('wagtailimages', '0026_delete_uploadedimage'),
    ]

    operations = [
        # HomePage - Main landing page
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('hero_title', models.CharField(blank=True, max_length=255)),
                ('hero_description', models.TextField(blank=True)),
                ('cta_title', models.CharField(blank=True, max_length=255)),
                ('cta_description', models.TextField(blank=True)),
                ('cta_button_text', models.CharField(blank=True, max_length=50)),
                ('cta_button_url', models.URLField(blank=True)),
                ('mission_statement', wagtail.fields.RichTextField(blank=True, help_text='Brief mission statement')),
                ('key_features', wagtail.fields.StreamField([('feature', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(max_length=100)), ('description', wagtail.blocks.TextBlock()), ('icon', wagtail.blocks.CharBlock(help_text='CSS class for icon', max_length=50, required=False))]))], blank=True, use_json_field=True)),
                ('testimonials', wagtail.fields.StreamField([('testimonial', wagtail.blocks.StructBlock([('quote', wagtail.blocks.TextBlock()), ('author', wagtail.blocks.CharBlock(max_length=100)), ('title', wagtail.blocks.CharBlock(max_length=100, required=False)), ('company', wagtail.blocks.CharBlock(max_length=100, required=False))]))], blank=True, use_json_field=True)),
                ('cta_section', wagtail.fields.RichTextField(blank=True, help_text='Call to action section content')),
                ('faq', wagtail.fields.RichTextField(blank=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # BlogIndexPage - Blog listing page
        migrations.CreateModel(
            name='BlogIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('introduction', wagtail.fields.RichTextField(blank=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', wagtail.contrib.routable_page.models.RoutablePageMixin),
        ),

        # BlogPost - Individual blog posts
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('date', models.DateField()),
                ('summary', models.TextField(blank=True, max_length=500)),
                ('author', models.CharField(max_length=255)),
                ('body', wagtail.fields.StreamField([('paragraph', wagtail.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.blocks.BlockQuoteBlock()), ('code', wagtail.blocks.TextBlock())], blank=True, use_json_field=True)),
                ('featured_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # SolutionsPage - Solutions overview
        migrations.CreateModel(
            name='SolutionsPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('body', wagtail.fields.RichTextField(blank=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # PRIDDQPage - PRIDDQ methodology page
        migrations.CreateModel(
            name='PRIDDQPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('body', wagtail.fields.RichTextField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('methodology', wagtail.fields.RichTextField(blank=True, help_text='Detailed methodology for PRIDDQ calculations')),
                ('metrics_description', wagtail.fields.RichTextField(blank=True, help_text='Description of metrics and what they mean')),
                ('data_sources', wagtail.fields.RichTextField(blank=True, help_text='Information about data sources used')),
                ('update_frequency', models.CharField(blank=True, default='Monthly', help_text='How often the data is updated', max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # EncyclopediaIndexPage - Encyclopedia listing
        migrations.CreateModel(
            name='EncyclopediaIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('introduction', wagtail.fields.RichTextField(blank=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # EncyclopediaEntry - Individual encyclopedia entries
        migrations.CreateModel(
            name='EncyclopediaEntry',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('summary', wagtail.fields.RichTextField(blank=True, help_text='Brief summary of the entry')),
                ('body', wagtail.fields.RichTextField()),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags', max_length=500)),
                ('related_terms', wagtail.fields.RichTextField(blank=True, help_text='Related terms and cross-references')),
                ('sources', wagtail.fields.RichTextField(blank=True, help_text='Sources and references')),
                ('featured_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
                ('last_reviewed', models.DateTimeField(auto_now=True)),
                ('difficulty_level', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # AdvisorPage - For advisor-specific content
        migrations.CreateModel(
            name='AdvisorPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('hero_title', models.CharField(blank=True, max_length=255)),
                ('hero_description', models.TextField(blank=True)),
                ('features_section', wagtail.fields.RichTextField(blank=True)),
                ('pricing_section', wagtail.fields.RichTextField(blank=True)),
                ('cta_section', wagtail.fields.RichTextField(blank=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'ordering': ['title'],
            },
            bases=('wagtailcore.page',),
        ),

        # StrategyPage - Individual strategy pages
        migrations.CreateModel(
            name='StrategyPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('description', wagtail.fields.RichTextField(blank=True)),
                ('methodology', wagtail.fields.RichTextField(blank=True)),
                ('performance_summary', wagtail.fields.RichTextField(blank=True)),
                ('holdings_preview', wagtail.fields.RichTextField(blank=True)),
                ('inception_date', models.DateField(blank=True, null=True)),
                ('hero_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # ContactFormPage - Contact form functionality
        migrations.CreateModel(
            name='ContactFormPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('introduction', wagtail.fields.RichTextField(blank=True)),
                ('thank_you_text', wagtail.fields.RichTextField(blank=True)),
                ('contact_email', models.EmailField(help_text='Email address that form submissions will be sent to')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),

        # Add tagging relationship for BlogPost
        migrations.CreateModel(
            name='BlogPostTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='public_site.blogpost')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='public_site_blogposttag_items', to='taggit.tag')),
            ],
            options={
                'abstract': False,
            },
        ),

        # MediaPage - Media/Press page
        migrations.CreateModel(
            name='MediaPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro_text', wagtail.fields.RichTextField(blank=True, default='<p>Media coverage, press releases, and company news.</p>')),
                ('press_kit_title', models.CharField(blank=True, default='Press Kit', max_length=200)),
                ('press_kit_description', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'verbose_name': 'Media Page',
            },
            bases=('wagtailcore.page',),
        ),

        # MediaItem - Individual media/press items
        migrations.CreateModel(
            name='MediaItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(max_length=300)),
                ('description', wagtail.fields.RichTextField(blank=True)),
                ('publication', models.CharField(blank=True, help_text='Publication name', max_length=200)),
                ('publication_date', models.DateField(blank=True, null=True)),
                ('external_url', models.URLField(blank=True, help_text='Link to external article/coverage')),
                ('featured', models.BooleanField(default=False, help_text='Feature this media item at the top')),
                ('page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_items', to='public_site.mediapage')),
            ],
            options={
                'ordering': ['-featured', '-publication_date'],
            },
            bases=(models.Model,),
        ),

        # Add tags field to BlogPost
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='public_site.BlogPostTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
