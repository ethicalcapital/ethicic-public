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
        blank=True,
        default="<p>Stay updated with the latest insights on ethical investing and portfolio management.</p>"
    )
    
    benefits_title = models.CharField(
        max_length=200,
        default="Why Subscribe?",
        blank=True
    )
    
    benefits_text = RichTextField(
        blank=True,
        default="""<ul>
            <li>Monthly market insights and ethical investing trends</li>
            <li>Research updates and portfolio strategy discussions</li>
            <li>Early access to new features and investment opportunities</li>
            <li>Exclusive content not available on the website</li>
        </ul>"""
    )
    
    privacy_text = RichTextField(
        blank=True,
        default="<p>We respect your privacy. Your email will only be used for our newsletter and you can unsubscribe at any time.</p>"
    )
    
    content_panels: ClassVar[list] = Page.content_panels + [
        FieldPanel("intro_text"),
        FieldPanel("benefits_title"),
        FieldPanel("benefits_text"),
        FieldPanel("privacy_text"),
    ]
    
    class Meta:
        verbose_name = "Newsletter Page"


class AccessibilityPage(Page):
    """Accessibility statement page."""
    
    template = "public_site/accessibility_page.html"
    
    intro_text = RichTextField(
        blank=True,
        default="<p>Ethical Capital is committed to ensuring digital accessibility for people with disabilities. We are continually improving the user experience for everyone and applying the relevant accessibility standards.</p>"
    )
    
    standards_text = RichTextField(
        blank=True,
        default="""<h2>Conformance Status</h2>
        <p>The Web Content Accessibility Guidelines (WCAG) defines requirements for designers and developers to improve accessibility for people with disabilities. It defines three levels of conformance: Level A, Level AA, and Level AAA. Ethical Capital is partially conformant with WCAG 2.1 level AA. Partially conformant means that some parts of the content do not fully conform to the accessibility standard.</p>"""
    )
    
    features_text = RichTextField(
        blank=True,
        default="""<h2>Accessibility Features</h2>
        <ul>
            <li>Keyboard navigation support throughout the site</li>
            <li>ARIA labels for screen reader compatibility</li>
            <li>High contrast mode support</li>
            <li>Resizable text without loss of functionality</li>
            <li>Alternative text for all informative images</li>
            <li>Consistent navigation structure</li>
            <li>Clear focus indicators</li>
        </ul>"""
    )
    
    feedback_text = RichTextField(
        blank=True,
        default="""<h2>Feedback</h2>
        <p>We welcome your feedback on the accessibility of Ethical Capital. Please let us know if you encounter accessibility barriers:</p>
        <ul>
            <li>Email: <a href="mailto:accessibility@ethicic.com">accessibility@ethicic.com</a></li>
            <li>Contact form: <a href="/contact/">Contact us</a></li>
        </ul>
        <p>We try to respond to feedback within 2 business days.</p>"""
    )
    
    technical_text = RichTextField(
        blank=True,
        default="""<h2>Technical Specifications</h2>
        <p>Accessibility of Ethical Capital relies on the following technologies to work with the particular combination of web browser and any assistive technologies or plugins installed on your computer:</p>
        <ul>
            <li>HTML</li>
            <li>CSS</li>
            <li>JavaScript</li>
            <li>ARIA</li>
        </ul>"""
    )
    
    limitations_text = RichTextField(
        blank=True,
        default="""<h2>Known Limitations</h2>
        <p>Despite our best efforts to ensure accessibility of Ethical Capital, there may be some limitations. Below is a description of known limitations:</p>
        <ul>
            <li>Some older PDF documents may not be fully accessible. We are working to update these.</li>
            <li>Some third-party content may not meet accessibility standards.</li>
            <li>Some interactive charts may require additional assistance for screen reader users.</li>
        </ul>"""
    )
    
    content_panels: ClassVar[list] = Page.content_panels + [
        FieldPanel("intro_text"),
        FieldPanel("standards_text"),
        FieldPanel("features_text"),
        FieldPanel("feedback_text"),
        FieldPanel("technical_text"),
        FieldPanel("limitations_text"),
    ]
    
    class Meta:
        verbose_name = "Accessibility Page"