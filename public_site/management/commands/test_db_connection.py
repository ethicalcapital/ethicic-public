"""
Test database connections with SSL certificates
"""
import os

import psycopg2
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Test database connections and SSL configuration"

    def handle(self, *args, **options):
        self.stdout.write("Testing database connections...\n")

        # Test each configured database
        for db_name in connections:
            self.stdout.write(f"Testing {db_name} database...")

            try:
                connection = connections[db_name]
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()

                self.stdout.write(
                    self.style.SUCCESS(f"✓ {db_name}: Connected successfully")
                )

                # Show connection details for PostgreSQL databases
                if "postgresql" in connection.settings_dict.get("ENGINE", ""):
                    cursor = connection.cursor()

                    # Check SSL status
                    cursor.execute("SELECT ssl_is_used()")
                    ssl_used = cursor.fetchone()[0]

                    if ssl_used:
                        cursor.execute("SELECT ssl_version()")
                        ssl_version = cursor.fetchone()[0]
                        self.stdout.write(f"  SSL: {ssl_version}")

                        # Show certificate info if available
                        cursor.execute(
                            """
                            SELECT ssl_client_cert_present(),
                                   ssl_cipher()
                        """
                        )
                        cert_present, cipher = cursor.fetchone()
                        self.stdout.write(f"  Cipher: {cipher}")
                        if cert_present:
                            self.stdout.write("  Client certificate: Present")
                    else:
                        self.stdout.write(self.style.WARNING("  SSL: Not in use"))

                    # Show connection options
                    options = connection.settings_dict.get("OPTIONS", {})
                    if options:
                        self.stdout.write("  Connection options:")
                        for key, value in options.items():
                            if "cert" in key or "key" in key:
                                # Don't show full paths for security
                                value = "***" if value else "Not set"
                            self.stdout.write(f"    {key}: {value}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ {db_name}: {e}"))

        # Test raw connection with environment variables
        self.stdout.write("\nTesting raw PostgreSQL connection...")
        if os.getenv("UBI_DATABASE_URL"):
            try:
                # Parse the URL manually to test SSL options
                import urllib.parse

                url = urllib.parse.urlparse(os.getenv("UBI_DATABASE_URL"))

                conn_params = {
                    "host": url.hostname,
                    "port": url.port or 5432,
                    "database": url.path[1:],
                    "user": url.username,
                    "password": url.password,
                }

                # Add SSL options following garden app pattern
                conn_params["sslmode"] = "require"
                conn_params["connect_timeout"] = 10

                # Check for SSL certificate
                ssl_cert_paths = [
                    os.getenv("SSL_ROOT_CERT"),
                    os.getenv("DB_CA_CERT_PATH"),
                    "/app/config/ssl/ubicloud-root-ca.pem",
                    "./config/ssl/ubicloud-root-ca.pem",
                ]

                for cert_path in ssl_cert_paths:
                    if cert_path and os.path.exists(cert_path):
                        conn_params["sslrootcert"] = cert_path
                        self.stdout.write(f"  Using SSL certificate: {cert_path}")
                        break

                # Debug connection parameters
                self.stdout.write("  Connection parameters:")
                self.stdout.write(f'    Host: {conn_params["host"]}')
                self.stdout.write(f'    Port: {conn_params["port"]}')
                self.stdout.write(f'    Database: {conn_params["database"]}')
                self.stdout.write(f'    User: {conn_params["user"]}')
                self.stdout.write(f'    SSL Mode: {conn_params["sslmode"]}')

                conn = psycopg2.connect(**conn_params)
                cur = conn.cursor()
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]

                self.stdout.write(self.style.SUCCESS("✓ Raw connection successful"))
                self.stdout.write(f'  PostgreSQL version: {version.split(",")[0]}')

                conn.close()

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Raw connection failed: {e}"))
