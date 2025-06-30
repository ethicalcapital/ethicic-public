#!/usr/bin/env python
"""
Django management command to safely import ALL data from Ubicloud
Handles schema differences between environments
"""
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, Site
from public_site.models import MediaItem, SupportTicket
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Import ALL content from Ubicloud database'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("IMPORTING ALL CONTENT FROM UBICLOUD")
        self.stdout.write("=" * 60)
        
        # Check if we have Ubicloud connection
        if 'ubicloud' not in connections:
            self.stdout.write(self.style.ERROR('Ubicloud database not configured!'))
            return
        
        ubicloud_conn = connections['ubicloud']
        
        # Use Django's model imports to handle schema differences
        self._import_pages_django_style(ubicloud_conn)
        self._import_media_items()
        self._import_support_tickets()
        
        # Fix site configuration
        self._fix_site_config()
        
        # Show summary
        self._show_summary()

    def _import_pages_django_style(self, conn):
        """Import pages using Django models to handle schema differences"""
        self.stdout.write("\n📄 Importing Pages...")
        
        # Map of model names to actual model classes
        from public_site import models as ps_models
        
        model_map = {
            'homepage': ps_models.HomePage,
            'aboutpage': ps_models.AboutPage,
            'contactpage': ps_models.ContactPage,
            'blogindexpage': ps_models.BlogIndexPage,
            'blogpost': ps_models.BlogPost,
            'faqpage': ps_models.FAQPage,
            'faqarticle': ps_models.FAQArticle,
            'encyclopediaindexpage': ps_models.EncyclopediaIndexPage,
            'encyclopediaentry': ps_models.EncyclopediaEntry,
            'strategylistpage': ps_models.StrategyListPage,
            'strategypage': ps_models.StrategyPage,
            'mediapage': ps_models.MediaPage,
            'legalpage': ps_models.LegalPage,
            'pricingpage': ps_models.PricingPage,
            'processpage': ps_models.ProcessPage,
            'researchpage': ps_models.ResearchPage,
            'onboardingpage': ps_models.OnboardingPage,
            'consultationpage': ps_models.ConsultationPage,
            'criteriapage': ps_models.CriteriaPage,
            'guidepage': ps_models.GuidePage,
            'solutionspage': ps_models.SolutionsPage,
            'advisorpage': ps_models.AdvisorPage,
            'institutionalpage': ps_models.InstitutionalPage,
            'priddqpage': ps_models.PRIDDQPage,
        }
        
        # First pass: Create all pages
        with conn.cursor() as cursor:
            # Get pages ordered by path to maintain hierarchy
            cursor.execute("""
                SELECT 
                    p.id, p.path, p.depth, p.title, p.slug, 
                    p.url_path, p.seo_title, p.search_description,
                    p.show_in_menus, p.first_published_at,
                    ct.model
                FROM wagtailcore_page p
                JOIN django_content_type ct ON p.content_type_id = ct.id
                WHERE ct.app_label = 'public_site'
                ORDER BY p.path
            """)
            
            pages = cursor.fetchall()
            self.stdout.write(f"Found {len(pages)} pages to import")
            
            # Track mapping of old IDs to new pages
            id_mapping = {}
            
            for page_data in pages:
                (old_id, path, depth, title, slug, url_path, 
                 seo_title, search_description, show_in_menus, 
                 first_published_at, model_name) = page_data
                
                # Skip if already exists
                if Page.objects.filter(slug=slug).exists():
                    existing = Page.objects.get(slug=slug)
                    id_mapping[old_id] = existing.id
                    self.stdout.write(f"  ✓ Already exists: {title}")
                    continue
                
                # Get model class
                ModelClass = model_map.get(model_name)
                if not ModelClass:
                    self.stdout.write(f"  ⚠️  Unknown model: {model_name}")
                    continue
                
                # Get model-specific data
                cursor.execute(f"""
                    SELECT * FROM public_site_{model_name}
                    WHERE page_ptr_id = %s
                """, [old_id])
                
                model_row = cursor.fetchone()
                if not model_row:
                    self.stdout.write(f"  ⚠️  No data for: {title}")
                    continue
                
                # Get column names
                model_columns = [col[0] for col in cursor.description]
                model_dict = dict(zip(model_columns, model_row))
                
                # Remove page_ptr_id as it's handled by Django
                model_dict.pop('page_ptr_id', None)
                
                # Create the page
                try:
                    # Find parent based on path
                    if len(path) > 4:
                        parent_path = path[:-4]
                        parent = Page.objects.filter(path=parent_path).first()
                    else:
                        parent = Page.objects.get(depth=1)  # Root
                    
                    if not parent:
                        self.stdout.write(f"  ⚠️  No parent for: {title}")
                        continue
                    
                    # Filter out fields that don't exist in the model
                    valid_fields = {f.name for f in ModelClass._meta.fields}
                    filtered_dict = {
                        k: v for k, v in model_dict.items() 
                        if k in valid_fields
                    }
                    
                    # Create the page instance
                    page = ModelClass(
                        title=title,
                        slug=slug,
                        seo_title=seo_title or '',
                        search_description=search_description or '',
                        show_in_menus=show_in_menus or False,
                        **filtered_dict
                    )
                    
                    # Add as child and publish
                    parent.add_child(instance=page)
                    
                    # Update timestamps if available
                    if first_published_at:
                        page.first_published_at = first_published_at
                        page.save(update_fields=['first_published_at'])
                    
                    page.save_revision().publish()
                    
                    id_mapping[old_id] = page.id
                    self.stdout.write(f"  ✓ Created: {title} ({model_name})")
                    
                except Exception as e:
                    self.stdout.write(f"  ❌ Failed: {title} - {str(e)}")

    def _import_media_items(self):
        """Import all media items"""
        self.stdout.write("\n📺 Importing Media Items...")
        
        try:
            items = MediaItem.objects.using('ubicloud').all()
            created = 0
            
            for item in items:
                if not MediaItem.objects.filter(title=item.title).exists():
                    MediaItem.objects.create(
                        title=item.title,
                        url=item.url,
                        source=item.source,
                        published_date=item.published_date,
                        description=item.description,
                        featured=item.featured,
                        order=item.order
                    )
                    created += 1
            
            self.stdout.write(f"✓ Created {created} media items")
            
        except Exception as e:
            self.stdout.write(f"❌ Media import failed: {e}")

    def _import_support_tickets(self):
        """Import support tickets with schema mapping"""
        self.stdout.write("\n🎫 Importing Support Tickets...")
        
        conn = connections['ubicloud']
        
        with conn.cursor() as cursor:
            # Get column names for proper mapping
            cursor.execute("SELECT * FROM public_site_supportticket LIMIT 0")
            columns = [col[0] for col in cursor.description]
            
            # Now get all tickets
            cursor.execute("SELECT * FROM public_site_supportticket")
            tickets = cursor.fetchall()
            
            created = 0
            for row in tickets:
                ticket_dict = dict(zip(columns, row))
                
                # Map fields properly
                try:
                    # Check what fields our local model has
                    local_fields = {f.name for f in SupportTicket._meta.fields}
                    
                    # Create ticket with available fields
                    ticket_data = {
                        'title': ticket_dict.get('title', 'Untitled'),
                        'subject': ticket_dict.get('subject', ticket_dict.get('title', 'No subject')),
                        'message': ticket_dict.get('message', ticket_dict.get('description', '')),
                        'status': ticket_dict.get('status', 'open'),
                        'priority': ticket_dict.get('priority', 'medium'),
                        'name': ticket_dict.get('name', ticket_dict.get('created_by', 'Unknown')),
                        'email': ticket_dict.get('email', 'noemail@example.com'),
                        'created_at': ticket_dict.get('created_at', datetime.now()),
                        'updated_at': ticket_dict.get('updated_at', datetime.now()),
                    }
                    
                    # Add optional fields if they exist
                    if 'company' in local_fields and 'company' in ticket_dict:
                        ticket_data['company'] = ticket_dict['company']
                    if 'notes' in local_fields and 'notes' in ticket_dict:
                        ticket_data['notes'] = ticket_dict['notes']
                    if 'resolved_at' in local_fields and 'resolved_at' in ticket_dict:
                        ticket_data['resolved_at'] = ticket_dict['resolved_at']
                    if 'ticket_type' in local_fields and 'category' in ticket_dict:
                        ticket_data['ticket_type'] = ticket_dict['category']
                    
                    # Check if already exists by title
                    if not SupportTicket.objects.filter(title=ticket_data['title']).exists():
                        SupportTicket.objects.create(**ticket_data)
                        created += 1
                        
                except Exception as e:
                    self.stdout.write(f"  ⚠️  Failed ticket: {e}")
            
            self.stdout.write(f"✓ Created {created} support tickets")

    def _fix_site_config(self):
        """Ensure site is properly configured"""
        self.stdout.write("\n🔧 Fixing site configuration...")
        
        site = Site.objects.first()
        home = Page.objects.filter(slug='home').first()
        
        if site and home:
            site.root_page = home
            site.hostname = 'localhost'
            site.port = 8000
            site.save()
            self.stdout.write("✓ Site configured with homepage as root")

    def _show_summary(self):
        """Show import summary"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 IMPORT SUMMARY")
        self.stdout.write(f"  Pages: {Page.objects.count()}")
        self.stdout.write(f"  Media Items: {MediaItem.objects.count()}")
        self.stdout.write(f"  Support Tickets: {SupportTicket.objects.count()}")
        
        # Show page tree
        self.stdout.write("\n📄 Page Tree:")
        for page in Page.objects.all().order_by('path')[:20]:  # Show first 20
            indent = "  " * (page.depth - 1)
            self.stdout.write(f"{indent}- {page.title} (/{page.slug}/)")
        
        if Page.objects.count() > 20:
            self.stdout.write(f"  ... and {Page.objects.count() - 20} more pages")
        
        self.stdout.write("\n✅ Import completed!")
        self.stdout.write("=" * 60)
