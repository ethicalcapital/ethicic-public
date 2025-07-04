"""Newsletter and Accessibility page models."""
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from typing import ClassVar


class NewsletterPage(Page):
    """Newsletter signup page."""
    
    template = "public_site/newsletter_page.html"
    
    intro_text = RichTextField(
        blank=True
    )
    
    benefits_title = models.CharField(
        max_length=200,
        blank=True
    )
    
    benefits_text = RichTextField(
        blank=True
    )
    
    privacy_text = RichTextField(
        blank=True
    )
    
    content_panels: ClassVar[list] = Page.content_panels + [
        FieldPanel("intro_text"),
        FieldPanel("benefits_title"),
        FieldPanel("benefits_text"),
        FieldPanel("privacy_text"),
    ]
    
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels
    
    class Meta:
        verbose_name = "Newsletter Page"


class AccessibilityPage(Page):
    """Accessibility statement page."""
    
    template = "public_site/accessibility_page.html"
    
    intro_text = RichTextField(
        blank=True
    )
    
    standards_text = RichTextField(
        blank=True
    )
    
    features_text = RichTextField(
        blank=True
    )
    
    feedback_text = RichTextField(
        blank=True
    )
    
    technical_text = RichTextField(
        blank=True
    )
    
    limitations_text = RichTextField(
        blank=True
    )
    
    content_panels: ClassVar[list] = Page.content_panels + [
        FieldPanel("intro_text"),
        FieldPanel("standards_text"),
        FieldPanel("features_text"),
        FieldPanel("feedback_text"),
        FieldPanel("technical_text"),
        FieldPanel("limitations_text"),
    ]
    
    promote_panels = Page.promote_panels
    settings_panels = Page.settings_panels
    
    class Meta:
        verbose_name = "Accessibility Page"