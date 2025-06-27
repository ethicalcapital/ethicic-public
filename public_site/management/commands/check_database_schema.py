"""
Check database schema and migrations status
"""
from django.core.management.base import BaseCommand
from django.db import connection, connections
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    help = 'Check database schema and migration status'

    def handle(self, *args, **options):
        self.stdout.write('\n=== Database Schema Check ===\n')
        
        # Check which database we're connected to
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("SELECT current_database(), current_schema(), version()")
                db, schema, version = cursor.fetchone()
                self.stdout.write(f'Database: {db}')
                self.stdout.write(f'Schema: {schema}')
                self.stdout.write(f'Version: {version}')
                
                # Check if we're connected to Ubicloud
                cursor.execute("SELECT inet_server_addr(), inet_server_port()")
                addr, port = cursor.fetchone()
                self.stdout.write(f'Server: {addr}:{port}')
            else:
                self.stdout.write(f'Database type: {connection.vendor}')
                self.stdout.write(f'Database name: {connection.settings_dict["NAME"]}')
        
        # Check migrations
        self.stdout.write('\n=== Migration Status ===')
        try:
            recorder = MigrationRecorder(connection)
            applied = recorder.applied_migrations()
            
            # Group by app
            apps = {}
            for (app, name) in applied:
                if app not in apps:
                    apps[app] = []
                apps[app].append(name)
            
            for app, migrations in sorted(apps.items()):
                self.stdout.write(f'\n{app}:')
                for migration in sorted(migrations):
                    self.stdout.write(f'  ✓ {migration}')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Could not check migrations: {e}'))
        
        # Check for public_site tables
        self.stdout.write('\n=== Public Site Tables ===')
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT table_name, 
                           (SELECT COUNT(*) FROM information_schema.columns 
                            WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'public_site_%'
                    ORDER BY table_name
                """)
            else:
                # SQLite
                cursor.execute("""
                    SELECT name, 
                           (SELECT COUNT(*) FROM pragma_table_info(m.name)) as column_count
                    FROM sqlite_master m
                    WHERE type='table' AND name LIKE 'public_site_%'
                    ORDER BY name
                """)
            
            tables = cursor.fetchall()
            if tables:
                for table, col_count in tables:
                    self.stdout.write(f'  - {table} ({col_count} columns)')
                    
                # Check specific table for required fields
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        AND table_name = 'public_site_homepage'
                        AND column_name IN ('hero_tagline', 'excluded_percentage', 'since_year')
                        ORDER BY ordinal_position
                    """)
                    found_columns = [col[0] for col in cursor.fetchall()]
                    if found_columns:
                        self.stdout.write(f'\nHomePage has these fields: {found_columns}')
                    else:
                        self.stdout.write(self.style.WARNING('\nHomePage missing expected fields!'))
            else:
                self.stdout.write('No public_site tables found')
        
        self.stdout.write('\n✓ Schema check complete\n')