"""
Database router for hybrid Ubicloud + local cache approach
"""

import logging

logger = logging.getLogger(__name__)


class HybridDatabaseRouter:
    """
    Routes database operations between Ubicloud (primary) and local cache.

    - Writes always go to Ubicloud
    - Reads for cached models come from local SQLite
    - Everything else goes to Ubicloud
    """

    def __init__(self):
        # Models that should be cached locally for performance
        # TEMPORARILY DISABLED - All models should use Ubicloud until cache sync is implemented
        self.CACHED_MODELS = set()
        # self.CACHED_MODELS = {
        #     'public_site.homepage',
        #     'public_site.blogpost',
        #     'public_site.mediaitem',
        #     'public_site.encyclopediaentry',
        #     'wagtailcore.page',
        #     'wagtailcore.site',
        #     'taggit.tag',
        # }

        # Models that should always use remote database
        self.REMOTE_ONLY_MODELS = {
            "public_site.supportticket",  # Always fresh from Ubicloud
            "auth.user",  # User data should be centralized
            "sessions.session",  # Sessions in Redis anyway
        }

    def db_for_read(self, model, **hints):
        """Suggest database for read operations."""
        model_label = model._meta.label_lower

        # Use local cache for frequently accessed content
        if model_label in self.CACHED_MODELS:
            return "cache"

        # Use Ubicloud for everything else
        return "ubicloud"

    def db_for_write(self, model, **hints):
        """Suggest database for write operations."""
        model_label = model._meta.label_lower

        # Always write to Ubicloud first
        if model_label in self.REMOTE_ONLY_MODELS:
            return "ubicloud"

        # For cached models, we'll sync to cache after Ubicloud write
        return "ubicloud"

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between cached and remote models."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Control which models get migrated to which database."""
        if db == "cache":
            # Only migrate cached models to cache database
            if model_name:
                model_label = f"{app_label}.{model_name}"
                return model_label in self.CACHED_MODELS
            return app_label in ["public_site", "wagtailcore", "taggit"]

        if db == "ubicloud":
            # Migrate everything to Ubicloud (it's the source of truth)
            return True

        return None
