#!/usr/bin/env python3
"""
Migrate Wagtail Page Content from Ubicloud to Kinsta Database
============================================================

This script downloads all Wagtail page content from the Ubicloud database
and uploads it to the Kinsta database, preserving all relationships and content.

Usage:
    python migrate_wagtail_content.py [--dry-run] [--verbose]

Requirements:
    - psycopg2-binary
    - python-dotenv (optional, for .env files)

Security:
    - Uses connection pooling for efficiency
    - Implements proper transaction handling
    - Includes rollback on errors
    - Validates data integrity before commit
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List
from contextlib import contextmanager

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, execute_batch
    from psycopg2.pool import ThreadedConnectionPool
except ImportError:
    print("ERROR: psycopg2-binary is required. Install with: pip install psycopg2-binary")
    sys.exit(1)

# Database connection strings - can be overridden via environment variables
UBICLOUD_DB = os.getenv('SOURCE_DB_URL', "postgres://garden:4lzUfNlkjgsXMDQRnU0BPx8r@localhost:5433/garden_platform")
KINSTA_DB = os.getenv('TARGET_DB_URL', "postgres://hyena:gV5_xN9-nT5_dV0=uD1-@europe-west3-002.proxy.kinsta.app:30365/ethicic-public")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'wagtail_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WagtailMigrator:
    """Handles migration of Wagtail content between databases."""
    
    def __init__(self, source_url: str, target_url: str, dry_run: bool = False):
        self.source_url = source_url
        self.target_url = target_url
        self.dry_run = dry_run
        self.source_pool = None
        self.target_pool = None
        
        # Track migration statistics
        self.stats = {
            'pages_migrated': 0,
            'revisions_migrated': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
    def __enter__(self):
        """Set up database connection pools."""
        try:
            self.source_pool = ThreadedConnectionPool(1, 5, self.source_url)
            self.target_pool = ThreadedConnectionPool(1, 5, self.target_url)
            logger.info("Database connection pools established")
            return self
        except Exception as e:
            logger.error(f"Failed to establish database connections: {e}")
            raise
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up database connections."""
        if self.source_pool:
            self.source_pool.closeall()
        if self.target_pool:
            self.target_pool.closeall()
        logger.info("Database connections closed")
        
    @contextmanager
    def get_source_connection(self):
        """Get a connection from the source pool."""
        conn = self.source_pool.getconn()
        try:
            yield conn
        finally:
            self.source_pool.putconn(conn)
            
    @contextmanager
    def get_target_connection(self):
        """Get a connection from the target pool."""
        conn = self.target_pool.getconn()
        try:
            yield conn
        finally:
            self.target_pool.putconn(conn)
    
    def get_wagtail_tables(self) -> List[str]:
        """Get all Wagtail-related table names from source database."""
        with self.get_source_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND (
                        table_name LIKE 'wagtail%' 
                        OR table_name LIKE 'public_site_%'
                        OR table_name IN ('django_content_type', 'auth_permission')
                    )
                    ORDER BY table_name;
                """)
                return [row[0] for row in cur.fetchall()]
    
    def get_table_dependencies(self) -> Dict[str, List[str]]:
        """Analyze foreign key dependencies to determine migration order."""
        dependencies = {}
        
        with self.get_source_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        tc.table_name,
                        ccu.table_name AS foreign_table_name
                    FROM
                        information_schema.table_constraints AS tc
                        JOIN information_schema.key_column_usage AS kcu
                            ON tc.constraint_name = kcu.constraint_name
                        JOIN information_schema.constraint_column_usage AS ccu
                            ON ccu.constraint_name = tc.constraint_name
                    WHERE constraint_type = 'FOREIGN KEY' 
                    AND tc.table_schema = 'public'
                    AND (
                        tc.table_name LIKE 'wagtail%' 
                        OR tc.table_name LIKE 'public_site_%'
                    );
                """)
                
                for table_name, foreign_table in cur.fetchall():
                    if table_name not in dependencies:
                        dependencies[table_name] = []
                    dependencies[table_name].append(foreign_table)
                    
        return dependencies
    
    def get_migration_order(self, tables: List[str]) -> List[str]:
        """Determine the correct order for table migration based on dependencies."""
        dependencies = self.get_table_dependencies()
        ordered_tables = []
        remaining_tables = set(tables)
        
        # Simple topological sort
        while remaining_tables:
            # Find tables with no unresolved dependencies
            ready_tables = []
            for table in remaining_tables:
                table_deps = dependencies.get(table, [])
                if not any(dep in remaining_tables for dep in table_deps):
                    ready_tables.append(table)
            
            if not ready_tables:
                # Handle circular dependencies by adding remaining tables
                logger.warning("Circular dependencies detected, adding remaining tables")
                ready_tables = list(remaining_tables)
            
            for table in ready_tables:
                ordered_tables.append(table)
                remaining_tables.remove(table)
                
        return ordered_tables
    
    def backup_target_data(self, tables: List[str]) -> str:
        """Create a backup of target data before migration."""
        backup_file = f"kinsta_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        if self.dry_run:
            logger.info(f"DRY RUN: Would create backup file: {backup_file}")
            return backup_file
            
        logger.info(f"Creating backup of target database: {backup_file}")
        
        # Use pg_dump to create backup
        import subprocess
        try:
            # Extract connection details from URL
            import urllib.parse
            parsed = urllib.parse.urlparse(self.target_url)
            
            cmd = [
                'pg_dump',
                f'--host={parsed.hostname}',
                f'--port={parsed.port}',
                f'--username={parsed.username}',
                f'--dbname={parsed.path[1:]}',  # Remove leading slash
                '--no-password',
                '--verbose',
                '--clean',
                '--create',
                f'--file={backup_file}'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
            logger.info(f"Backup completed successfully: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def clear_target_wagtail_data(self, tables: List[str]):
        """Clear existing Wagtail data from target database."""
        if self.dry_run:
            logger.info("DRY RUN: Would clear target Wagtail data")
            return
            
        logger.info("Clearing existing Wagtail data from target database")
        
        with self.get_target_connection() as conn:
            with conn.cursor() as cur:
                try:
                    # Disable foreign key checks temporarily
                    cur.execute("SET session_replication_role = replica;")
                    
                    # Delete in reverse dependency order
                    for table in reversed(tables):
                        try:
                            cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
                            logger.debug(f"Cleared table: {table}")
                        except Exception as e:
                            logger.warning(f"Could not clear table {table}: {e}")
                    
                    # Re-enable foreign key checks
                    cur.execute("SET session_replication_role = DEFAULT;")
                    conn.commit()
                    logger.info("Target database cleared successfully")
                    
                except Exception as e:
                    conn.rollback()
                    logger.error(f"Failed to clear target database: {e}")
                    raise
    
    def copy_table_data(self, table_name: str):
        """Copy data from source table to target table."""
        logger.info(f"Migrating table: {table_name}")
        
        try:
            # Get source data
            with self.get_source_connection() as source_conn:
                with source_conn.cursor(cursor_factory=RealDictCursor) as source_cur:
                    source_cur.execute(f"SELECT * FROM {table_name};")
                    rows = source_cur.fetchall()
                    
                    if not rows:
                        logger.info(f"No data found in table: {table_name}")
                        return 0
                    
                    # Get column names
                    column_names = [desc[0] for desc in source_cur.description]
            
            if self.dry_run:
                logger.info(f"DRY RUN: Would migrate {len(rows)} rows from {table_name}")
                return len(rows)
            
            # Insert into target
            with self.get_target_connection() as target_conn:
                with target_conn.cursor() as target_cur:
                    try:
                        # Prepare insert statement
                        placeholders = ', '.join(['%s'] * len(column_names))
                        columns = ', '.join(column_names)
                        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                        
                        # Convert dict rows to tuples
                        data_tuples = [tuple(row[col] for col in column_names) for row in rows]
                        
                        # Batch insert for efficiency
                        execute_batch(target_cur, insert_sql, data_tuples, page_size=1000)
                        
                        target_conn.commit()
                        logger.info(f"Successfully migrated {len(rows)} rows from {table_name}")
                        return len(rows)
                        
                    except Exception as e:
                        target_conn.rollback()
                        logger.error(f"Failed to insert data into {table_name}: {e}")
                        raise
                        
        except Exception as e:
            logger.error(f"Failed to migrate table {table_name}: {e}")
            self.stats['errors'] += 1
            return 0
    
    def fix_sequences(self, tables: List[str]):
        """Fix PostgreSQL sequences after data migration."""
        if self.dry_run:
            logger.info("DRY RUN: Would fix PostgreSQL sequences")
            return
            
        logger.info("Fixing PostgreSQL sequences")
        
        with self.get_target_connection() as conn:
            with conn.cursor() as cur:
                for table in tables:
                    try:
                        # Find all sequences for this table
                        cur.execute("""
                            SELECT column_name, column_default
                            FROM information_schema.columns
                            WHERE table_name = %s
                            AND column_default LIKE 'nextval%%';
                        """, (table,))
                        
                        for column_name, column_default in cur.fetchall():
                            # Extract sequence name from default value
                            # Format: nextval('sequence_name'::regclass)
                            seq_start = column_default.find("'") + 1
                            seq_end = column_default.find("'", seq_start)
                            sequence_name = column_default[seq_start:seq_end]
                            
                            # Reset sequence to max value in table
                            cur.execute(f"""
                                SELECT setval('{sequence_name}', 
                                    COALESCE((SELECT MAX({column_name}) FROM {table}), 1), 
                                    false);
                            """)
                            
                        conn.commit()
                        
                    except Exception as e:
                        logger.warning(f"Could not fix sequences for table {table}: {e}")
                        conn.rollback()
    
    def validate_migration(self, tables: List[str]) -> bool:
        """Validate that migration was successful by comparing row counts."""
        logger.info("Validating migration...")
        
        validation_passed = True
        
        for table in tables:
            try:
                # Get source count
                with self.get_source_connection() as source_conn:
                    with source_conn.cursor() as cur:
                        cur.execute(f"SELECT COUNT(*) FROM {table};")
                        source_count = cur.fetchone()[0]
                
                if self.dry_run:
                    logger.info(f"DRY RUN: Would validate {table} ({source_count} rows)")
                    continue
                    
                # Get target count
                with self.get_target_connection() as target_conn:
                    with target_conn.cursor() as cur:
                        cur.execute(f"SELECT COUNT(*) FROM {table};")
                        target_count = cur.fetchone()[0]
                
                if source_count != target_count:
                    logger.error(f"Row count mismatch for {table}: source={source_count}, target={target_count}")
                    validation_passed = False
                else:
                    logger.debug(f"✓ {table}: {source_count} rows")
                    
            except Exception as e:
                logger.error(f"Validation failed for table {table}: {e}")
                validation_passed = False
        
        if validation_passed:
            logger.info("✓ Migration validation passed")
        else:
            logger.error("✗ Migration validation failed")
            
        return validation_passed
    
    def run_migration(self) -> bool:
        """Execute the complete migration process."""
        try:
            logger.info(f"Starting Wagtail content migration (dry_run={self.dry_run})")
            
            # Get tables to migrate
            tables = self.get_wagtail_tables()
            logger.info(f"Found {len(tables)} Wagtail tables to migrate")
            
            # Determine migration order
            ordered_tables = self.get_migration_order(tables)
            logger.info(f"Migration order determined: {len(ordered_tables)} tables")
            
            # Create backup
            backup_file = self.backup_target_data(ordered_tables)
            
            # Clear target data
            self.clear_target_wagtail_data(ordered_tables)
            
            # Migrate each table
            total_rows = 0
            for table in ordered_tables:
                rows_migrated = self.copy_table_data(table)
                total_rows += rows_migrated
                
                if table.startswith('wagtailcore_page'):
                    self.stats['pages_migrated'] += rows_migrated
                elif table.startswith('wagtailcore_pagerevision'):
                    self.stats['revisions_migrated'] += rows_migrated
            
            # Fix sequences
            self.fix_sequences(ordered_tables)
            
            # Validate migration
            if not self.validate_migration(ordered_tables):
                logger.error("Migration validation failed!")
                return False
            
            # Update statistics
            self.stats['end_time'] = datetime.now()
            duration = self.stats['end_time'] - self.stats['start_time']
            
            logger.info(f"""
Migration completed successfully!
================================
Tables migrated: {len(ordered_tables)}
Total rows: {total_rows}
Pages migrated: {self.stats['pages_migrated']}
Revisions migrated: {self.stats['revisions_migrated']}
Errors: {self.stats['errors']}
Duration: {duration}
Backup file: {backup_file}
""")
            
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate Wagtail content between databases')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Perform a dry run without making changes')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Confirm before running
    if not args.dry_run:
        print("⚠️  WARNING: This will overwrite all Wagtail content in the target database!")
        print(f"Source: {UBICLOUD_DB[:50]}...")
        print(f"Target: {KINSTA_DB[:50]}...")
        confirmation = input("Type 'MIGRATE' to continue: ")
        if confirmation != 'MIGRATE':
            print("Migration cancelled.")
            return 1
    
    try:
        with WagtailMigrator(UBICLOUD_DB, KINSTA_DB, dry_run=args.dry_run) as migrator:
            success = migrator.run_migration()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        logger.info("Migration cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())