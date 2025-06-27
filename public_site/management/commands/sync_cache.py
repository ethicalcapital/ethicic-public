"""
Sync data from Ubicloud to local cache database
"""
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.apps import apps
from public_site.db_router import HybridDatabaseRouter
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync cached models from Ubicloud to local SQLite cache'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Sync only a specific model (e.g., public_site.HomePage)'
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear cache before syncing'
        )
    
    def handle(self, *args, **options):
        router = HybridDatabaseRouter()
        
        # Get models to sync
        if options['model']:
            models_to_sync = [options['model'].lower()]
        else:
            models_to_sync = router.CACHED_MODELS
        
        self.stdout.write('Starting cache sync...')
        
        for model_label in models_to_sync:
            try:
                app_label, model_name = model_label.split('.')
                model = apps.get_model(app_label, model_name)
                
                # Clear existing cache if requested
                if options['clear_cache']:
                    model.objects.using('cache').all().delete()
                    self.stdout.write(f'Cleared cache for {model_label}')
                
                # Get data from Ubicloud
                remote_objects = model.objects.using('ubicloud').all()
                count = remote_objects.count()
                
                if count == 0:
                    self.stdout.write(f'No {model_label} objects to sync')
                    continue
                
                # Sync to cache in batches
                batch_size = 100
                synced = 0
                
                with transaction.atomic(using='cache'):
                    for obj in remote_objects.iterator(chunk_size=batch_size):
                        # Save to cache database
                        obj.save(using='cache')
                        synced += 1
                        
                        if synced % batch_size == 0:
                            self.stdout.write(f'Synced {synced}/{count} {model_label} objects...')
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Synced {synced} {model_label} objects to cache')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to sync {model_label}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Cache sync completed!')
        )