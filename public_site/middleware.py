"""
Middleware for cache management in hybrid database setup
"""
import logging
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class CacheInvalidationMiddleware:
    """
    Middleware to handle cache invalidation for the hybrid database approach.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response


# Signal handlers to sync changes to cache database
@receiver(post_save)
def sync_to_cache_on_save(sender, instance, created, **kwargs):
    """Sync model instances to cache database when saved to Ubicloud."""
    from public_site.db_router import HybridDatabaseRouter
    
    router = HybridDatabaseRouter()
    model_label = f"{sender._meta.app_label}.{sender._meta.model_name}"
    
    # Only sync cached models
    if model_label in router.CACHED_MODELS:
        try:
            # Save to cache database
            instance.save(using='cache')
            logger.info(f"Synced {model_label} id={instance.pk} to cache")
            
            # Invalidate related cache keys
            cache_key = f"{model_label}:{instance.pk}"
            cache.delete(cache_key)
            
        except Exception as e:
            logger.error(f"Failed to sync {model_label} to cache: {e}")


@receiver(post_delete)
def remove_from_cache_on_delete(sender, instance, **kwargs):
    """Remove model instances from cache database when deleted from Ubicloud."""
    from public_site.db_router import HybridDatabaseRouter
    
    router = HybridDatabaseRouter()
    model_label = f"{sender._meta.app_label}.{sender._meta.model_name}"
    
    # Only handle cached models
    if model_label in router.CACHED_MODELS:
        try:
            # Delete from cache database
            sender.objects.using('cache').filter(pk=instance.pk).delete()
            logger.info(f"Removed {model_label} id={instance.pk} from cache")
            
            # Invalidate related cache keys
            cache_key = f"{model_label}:{instance.pk}"
            cache.delete(cache_key)
            
        except Exception as e:
            logger.error(f"Failed to remove {model_label} from cache: {e}")