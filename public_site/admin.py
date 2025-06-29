from typing import ClassVar


"""
Django admin configuration for public site models.
CRITICAL: All models must be registered for proper content management.
"""

from django.contrib import admin

from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    """Admin interface for support tickets - CRITICAL for customer service."""

    list_display: ClassVar[list] = [
        "id",
        "name",
        "email",
        "company",
        "subject",
        "ticket_type",
        "status",
        "priority",
        "created_at",
        "updated_at",
    ]
    list_filter: ClassVar[list] = ["status", "ticket_type", "priority", "created_at", "updated_at"]
    search_fields: ClassVar[list] = ["name", "email", "company", "subject", "message"]
    readonly_fields: ClassVar[list] = ["created_at", "updated_at"]
    list_per_page = 25
    ordering: ClassVar[list] = ["-created_at"]

    fieldsets = (
        (
            "Contact Information",
            {"fields": ("name", "email", "company")},
        ),
        ("Inquiry Details", {"fields": ("ticket_type", "subject", "message")}),
        (
            "Status & Priority",
            {"fields": ("status", "priority", "resolved_at")},
        ),
        (
            "Internal",
            {"fields": ("notes",)},
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            },
        ),
    )

    actions: ClassVar[list] = ["mark_resolved", "mark_in_progress", "mark_closed"]

    def mark_resolved(self, request, queryset):
        """Bulk action to mark tickets as resolved."""
        updated = queryset.update(status="resolved")
        self.message_user(request, f"{updated} tickets marked as resolved.")
    mark_resolved.short_description = "Mark selected tickets as resolved"

    def mark_in_progress(self, request, queryset):
        """Bulk action to mark tickets as in progress."""
        updated = queryset.update(status="in_progress")
        self.message_user(request, f"{updated} tickets marked as in progress.")
    mark_in_progress.short_description = "Mark selected tickets as in progress"

    def mark_closed(self, request, queryset):
        """Bulk action to mark tickets as closed."""
        updated = queryset.update(status="closed")
        self.message_user(request, f"{updated} tickets marked as closed.")
    mark_closed.short_description = "Mark selected tickets as closed"

