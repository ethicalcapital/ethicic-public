"""Standalone constants for public site deployment.

Extracted from shared.constants to eliminate dependencies.
"""


class ContactStatus:
    """Contact status constants for standalone deployment."""

    COLD_LEAD = "COLD_LEAD"
    WARM_LEAD = "WARM_LEAD"
    PROSPECT = "PROSPECT"
    CLIENT = "CLIENT"
    FORMER_CLIENT = "FORMER_CLIENT"
    FRIEND = "FRIEND"
    VENDOR = "VENDOR"
    ARCHIVED = "ARCHIVED"

    @classmethod
    def choices(cls):
        """Django choices format."""
        return [
            (cls.COLD_LEAD, "Cold Lead"),
            (cls.WARM_LEAD, "Warm Lead"),
            (cls.PROSPECT, "Prospect"),
            (cls.CLIENT, "Client"),
            (cls.FORMER_CLIENT, "Former Client"),
            (cls.FRIEND, "Friend"),
            (cls.VENDOR, "Vendor"),
            (cls.ARCHIVED, "Archived"),
        ]


class ContactType:
    """Contact type constants for standalone deployment."""

    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"
    HOUSEHOLD = "HOUSEHOLD"

    @classmethod
    def choices(cls):
        """Django choices format."""
        return [
            (cls.INDIVIDUAL, "Individual"),
            (cls.COMPANY, "Company"),
            (cls.HOUSEHOLD, "Household"),
        ]


class PriorityLevel:
    """Priority level constants for standalone deployment."""

    VERY_LOW = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @classmethod
    def choices(cls):
        """Django choices format."""
        return [
            (cls.VERY_LOW, "Very Low"),
            (cls.LOW, "Low"),
            (cls.MEDIUM, "Medium"),
            (cls.HIGH, "High"),
            (cls.CRITICAL, "Critical"),
        ]


class InteractionType:
    """Interaction type constants for standalone deployment."""

    EMAIL = "EMAIL"
    EMAIL_RECEIVED = "EMAIL_RECEIVED"
    PHONE = "PHONE"
    DOCUMENT = "DOCUMENT"
    SMS = "SMS"
    MAIL = "MAIL"
    SOCIAL = "SOCIAL"
    MEETING = "MEETING"
    WEBSITE = "WEBSITE"
    NOTE = "NOTE"
    TASK = "TASK"

    @classmethod
    def choices(cls):
        """Django choices format."""
        return [
            (cls.EMAIL, "Email"),
            (cls.EMAIL_RECEIVED, "Email Received"),
            (cls.PHONE, "Phone"),
            (cls.DOCUMENT, "Document"),
            (cls.SMS, "SMS"),
            (cls.MAIL, "Mail"),
            (cls.SOCIAL, "Social Media"),
            (cls.MEETING, "Meeting"),
            (cls.WEBSITE, "Website"),
            (cls.NOTE, "Note"),
            (cls.TASK, "Task"),
        ]