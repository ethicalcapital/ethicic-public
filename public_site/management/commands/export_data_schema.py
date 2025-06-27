"""
Management command to export database schema for reference
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Export database schema for public site tables'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get all public_site tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'public_site_%'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            
            self.stdout.write("=== Public Site Database Schema ===\n")
            
            for (table_name,) in tables:
                self.stdout.write(f"\nTable: {table_name}")
                self.stdout.write("-" * (len(table_name) + 7))
                
                # Get column information
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position
                """, [table_name])
                
                columns = cursor.fetchall()
                
                for col in columns:
                    nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col[3]}" if col[3] else ""
                    self.stdout.write(
                        f"  {col[0]:<30} {col[1]:<20} {nullable}{default}"
                    )
            
            self.stdout.write("\n=== End Schema ===")
            
            # Also output sample SQL queries for reference
            self.stdout.write("\n=== Sample Import Queries ===")
            self.stdout.write("""
-- HomePage
SELECT id, title, slug, hero_title, hero_subtitle, body
FROM public_site_homepage
WHERE live = true;

-- BlogPost  
SELECT id, title, slug, subtitle, date, summary, author, body, updated_at
FROM public_site_blogpost
WHERE live = true
ORDER BY date DESC;

-- MediaItem
SELECT title, publication, url, date, excerpt, featured, created_at, updated_at
FROM public_site_mediaitem
ORDER BY date DESC;

-- SupportTicket
SELECT ticket_type, name, email, company, subject, message, 
       status, priority, created_at, updated_at, resolved_at, notes
FROM public_site_supportticket
WHERE created_at > NOW() - INTERVAL '90 days';
""")