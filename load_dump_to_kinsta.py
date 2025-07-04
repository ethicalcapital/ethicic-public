#!/usr/bin/env python3
"""
Load Database Dump to Kinsta Database
====================================

This script loads the local database dump file to the Kinsta database,
filtering for only Wagtail page content and related data.

Usage:
    python load_dump_to_kinsta.py [--dry-run] [--verbose] [--dump-file FILE]

Features:
    - Loads from local SQL dump file
    - Filters to only include Wagtail content
    - Creates backup before loading
    - Validates data integrity
    - Supports dry run mode

Requirements:
    - psycopg2-binary
    - Local SQL dump file
"""

import os
import sys
import re
import argparse
import logging
import subprocess
from datetime import datetime
from typing import List

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("ERROR: psycopg2-binary is required. Install with: pip install psycopg2-binary")
    sys.exit(1)

# Default database connection and dump file
DEFAULT_DUMP_FILE = "database_dump_20250629_210720.sql"
KINSTA_DB = "postgres://hyena:gV5_xN9-nT5_dV0=uD1-@europe-west3-002.proxy.kinsta.app:30365/ethicic-public"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'kinsta_load_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KinstaDumpLoader:
    """Loads database dump to Kinsta, filtering for Wagtail content only."""
    
    def __init__(self, dump_file: str, target_url: str, dry_run: bool = False, skip_backup: bool = False):
        self.dump_file = dump_file
        self.target_url = target_url
        self.dry_run = dry_run
        self.skip_backup = skip_backup
        
        # Track statistics
        self.stats = {
            'tables_processed': 0,
            'wagtail_tables': 0,
            'rows_inserted': 0,
            'start_time': datetime.now()
        }
        
    def validate_dump_file(self) -> bool:
        """Validate that the dump file exists and is readable."""
        if not os.path.exists(self.dump_file):
            logger.error(f"Dump file not found: {self.dump_file}")
            return False
            
        if not os.access(self.dump_file, os.R_OK):
            logger.error(f"Cannot read dump file: {self.dump_file}")
            return False
            
        # Check file size
        file_size = os.path.getsize(self.dump_file)
        logger.info(f"Dump file size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        return True
    
    def get_wagtail_tables_from_dump(self) -> List[str]:
        """Extract list of Wagtail tables from the dump file."""
        wagtail_tables = set()
        
        logger.info("Scanning dump file for Wagtail tables...")
        
        with open(self.dump_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Look for CREATE TABLE statements
                if line.strip().upper().startswith('CREATE TABLE'):
                    # Extract table name using regex
                    match = re.search(r'CREATE TABLE\s+(?:public\.)?(["\w]+)', line, re.IGNORECASE)
                    if match:
                        table_name = match.group(1).strip('"')
                        
                        # Check if it's a Wagtail-related table
                        if self.is_wagtail_table(table_name):
                            wagtail_tables.add(table_name)
                            logger.debug(f"Found Wagtail table: {table_name}")
                
                # Scan more thoroughly for CREATE TABLE statements
                if line_num > 50000 and len(wagtail_tables) > 10:
                    break
        
        sorted_tables = sorted(list(wagtail_tables))
        logger.info(f"Found {len(sorted_tables)} Wagtail tables in dump file")
        return sorted_tables
    
    def is_wagtail_table(self, table_name: str) -> bool:
        """Check if a table name is Wagtail-related."""
        wagtail_prefixes = [
            'wagtail',
            'public_site_',
            'taggit_',
        ]
        
        essential_tables = [
            'django_content_type',
            'auth_permission',
            'auth_group',
            'auth_group_permissions',
            'auth_user',
            'auth_user_groups',
            'auth_user_user_permissions',
        ]
        
        # Wagtail content types we definitely want
        wagtail_content_tables = [
            'django_migrations',  # For migration tracking
        ]
        
        table_lower = table_name.lower()
        
        # Check if it starts with any Wagtail prefix
        for prefix in wagtail_prefixes:
            if table_lower.startswith(prefix):
                return True
        
        # Check if it's an essential table
        if table_lower in essential_tables:
            return True
            
        # Check if it's a wagtail content table
        if table_lower in wagtail_content_tables:
            return True
            
        return False
    
    def create_filtered_dump(self, wagtail_tables: List[str]) -> str:
        """Create a filtered dump containing only Wagtail tables."""
        filtered_dump = f"wagtail_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        if self.dry_run:
            logger.info(f"DRY RUN: Would create filtered dump: {filtered_dump}")
            return filtered_dump
        
        logger.info(f"Creating filtered dump with {len(wagtail_tables)} tables...")
        
        with open(self.dump_file, 'r', encoding='utf-8', errors='ignore') as infile:
            with open(filtered_dump, 'w', encoding='utf-8') as outfile:
                
                # Write header comments
                outfile.write(f"""--
-- Filtered Wagtail Content Dump
-- Generated: {datetime.now().isoformat()}
-- Source: {self.dump_file}
-- Tables: {len(wagtail_tables)}
--

""")
                
                current_table = None
                in_wagtail_section = False
                copy_mode = False
                
                for line in infile:
                    line_upper = line.strip().upper()
                    
                    # Detect table sections
                    if line_upper.startswith('--'):
                        # Check if this is a table section header
                        for table in wagtail_tables:
                            if table.upper() in line.upper():
                                current_table = table
                                in_wagtail_section = True
                                outfile.write(line)
                                break
                        else:
                            if 'TABLE' in line_upper:
                                in_wagtail_section = False
                                current_table = None
                            if in_wagtail_section:
                                outfile.write(line)
                    
                    elif line_upper.startswith('CREATE TABLE'):
                        # Extract table name
                        match = re.search(r'CREATE TABLE\s+(?:public\.)?(["\w]+)', line, re.IGNORECASE)
                        if match:
                            table_name = match.group(1).strip('"')
                            if table_name in wagtail_tables:
                                current_table = table_name
                                in_wagtail_section = True
                                outfile.write(line)
                            else:
                                in_wagtail_section = False
                                current_table = None
                    
                    elif line_upper.startswith('COPY '):
                        # Check if this is for a Wagtail table
                        match = re.search(r'COPY\s+(?:public\.)?(["\w]+)', line, re.IGNORECASE)
                        if match:
                            table_name = match.group(1).strip('"')
                            if table_name in wagtail_tables:
                                copy_mode = True
                                in_wagtail_section = True
                                outfile.write(line)
                            else:
                                copy_mode = False
                                in_wagtail_section = False
                    
                    elif line.strip() == '\\.' and copy_mode:
                        # End of COPY data
                        outfile.write(line)
                        copy_mode = False
                        in_wagtail_section = False
                    
                    elif in_wagtail_section:
                        outfile.write(line)
                    
                    # Include sequences, constraints, and indexes for Wagtail tables
                    elif any(keyword in line_upper for keyword in ['ALTER TABLE', 'CREATE INDEX', 'CREATE SEQUENCE']):
                        for table in wagtail_tables:
                            if table.upper() in line.upper():
                                outfile.write(line)
                                break
        
        # Get file size
        filtered_size = os.path.getsize(filtered_dump)
        logger.info(f"Filtered dump created: {filtered_dump} ({filtered_size:,} bytes)")
        
        return filtered_dump
    
    def backup_kinsta_database(self) -> str:
        """Create backup of Kinsta database before loading."""
        backup_file = f"kinsta_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        if self.dry_run:
            logger.info(f"DRY RUN: Would create backup: {backup_file}")
            return backup_file
        
        logger.info("Creating backup of Kinsta database...")
        
        try:
            # Parse connection URL
            import urllib.parse
            parsed = urllib.parse.urlparse(self.target_url)
            
            # Use pg_dump to create backup
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
            
            backup_size = os.path.getsize(backup_file)
            logger.info(f"Backup created: {backup_file} ({backup_size:,} bytes)")
            
            return backup_file
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    def load_filtered_dump(self, filtered_dump: str) -> bool:
        """Load the filtered dump into Kinsta database."""
        if self.dry_run:
            logger.info(f"DRY RUN: Would load {filtered_dump} to Kinsta database")
            return True
        
        logger.info("Loading filtered dump to Kinsta database...")
        
        try:
            # Parse connection URL
            import urllib.parse
            parsed = urllib.parse.urlparse(self.target_url)
            
            # Use psql to load the dump
            cmd = [
                'psql',
                f'--host={parsed.hostname}',
                f'--port={parsed.port}',
                f'--username={parsed.username}',
                f'--dbname={parsed.path[1:]}',
                '--no-password',
                '--file', filtered_dump
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = parsed.password
            
            logger.info("Executing psql command...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Load failed: {result.stderr}")
                logger.error(f"stdout: {result.stdout}")
                return False
            
            logger.info("Load completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load dump: {e}")
            return False
    
    def validate_load(self, wagtail_tables: List[str]) -> bool:
        """Validate that the load was successful."""
        if self.dry_run:
            logger.info("DRY RUN: Would validate load")
            return True
        
        logger.info("Validating load...")
        
        try:
            with psycopg2.connect(self.target_url) as conn:
                with conn.cursor() as cur:
                    total_rows = 0
                    for table in wagtail_tables:
                        try:
                            cur.execute(f"SELECT COUNT(*) FROM {table};")
                            count = cur.fetchone()[0]
                            total_rows += count
                            logger.debug(f"✓ {table}: {count} rows")
                        except Exception as e:
                            logger.warning(f"Could not validate table {table}: {e}")
                    
                    logger.info(f"✓ Validation completed: {total_rows:,} total rows across {len(wagtail_tables)} tables")
                    self.stats['rows_inserted'] = total_rows
                    return True
                    
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
    
    def cleanup_temp_files(self, files: List[str]):
        """Clean up temporary files."""
        for file_path in files:
            if os.path.exists(file_path) and not self.dry_run:
                try:
                    os.remove(file_path)
                    logger.debug(f"Cleaned up: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not clean up {file_path}: {e}")
    
    def run_load(self) -> bool:
        """Execute the complete load process."""
        temp_files = []
        
        try:
            logger.info(f"Starting Kinsta database load (dry_run={self.dry_run})")
            logger.info(f"Source dump: {self.dump_file}")
            logger.info(f"Target database: {self.target_url[:50]}...")
            
            # Validate dump file
            if not self.validate_dump_file():
                return False
            
            # Get Wagtail tables from dump
            wagtail_tables = self.get_wagtail_tables_from_dump()
            if not wagtail_tables:
                logger.error("No Wagtail tables found in dump file")
                return False
            
            self.stats['wagtail_tables'] = len(wagtail_tables)
            
            # Create filtered dump
            filtered_dump = self.create_filtered_dump(wagtail_tables)
            temp_files.append(filtered_dump)
            
            # Create backup (unless skipped)
            if self.skip_backup:
                logger.info("Skipping backup creation")
                backup_file = "backup_skipped"
            else:
                backup_file = self.backup_kinsta_database()
            
            # Load filtered dump
            if not self.load_filtered_dump(filtered_dump):
                logger.error("Failed to load dump")
                return False
            
            # Validate load
            if not self.validate_load(wagtail_tables):
                logger.error("Load validation failed")
                return False
            
            # Update statistics
            self.stats['end_time'] = datetime.now()
            duration = self.stats['end_time'] - self.stats['start_time']
            
            logger.info(f"""
Load completed successfully!
===========================
Source dump: {self.dump_file}
Wagtail tables: {self.stats['wagtail_tables']}
Rows loaded: {self.stats['rows_inserted']:,}
Duration: {duration}
Backup file: {backup_file}
""")
            
            return True
            
        except Exception as e:
            logger.error(f"Load failed: {e}")
            return False
        finally:
            # Clean up temporary files
            self.cleanup_temp_files(temp_files)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Load database dump to Kinsta')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform a dry run without making changes')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--dump-file', default=DEFAULT_DUMP_FILE,
                       help=f'Path to dump file (default: {DEFAULT_DUMP_FILE})')
    parser.add_argument('--target-url', default=KINSTA_DB,
                       help='Target database URL')
    parser.add_argument('--yes', action='store_true',
                       help='Skip confirmation prompt')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip creating backup (useful for version mismatches)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Confirm before running
    if not args.dry_run and not args.yes:
        print("⚠️  WARNING: This will overwrite Wagtail content in the Kinsta database!")
        print(f"Source dump: {args.dump_file}")
        print(f"Target: {args.target_url[:50]}...")
        confirmation = input("Type 'LOAD' to continue: ")
        if confirmation != 'LOAD':
            print("Load cancelled.")
            return 1
    
    try:
        loader = KinstaDumpLoader(args.dump_file, args.target_url, dry_run=args.dry_run, skip_backup=args.skip_backup)
        success = loader.run_load()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("Load cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Load failed with error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())