"""
Cloudflare Images blocks for Wagtail StreamField.
Provides image blocks that integrate with Cloudflare Images for optimized delivery.
"""

import contextlib

from django.utils.html import format_html
from integrations.services.cloudflare_images_service import cloudflare_images
from wagtail import blocks
from wagtail.admin.widgets import AdminTextInput


class CloudflareImageChooserWidget(AdminTextInput):
    """Custom widget for choosing Cloudflare Images."""

    template_name = "wagtailadmin/widgets/cloudflare_image_chooser.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_files = [
            "js/cloudflare-image-chooser.js",
            "css/cloudflare-image-chooser.css",
        ]

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with upload and URL generation functionality."""
        if attrs is None:
            attrs = {}

        attrs.update(
            {
                "class": "cloudflare-image-input",
                "data-cloudflare-enabled": str(
                    cloudflare_images.is_configured()
                ).lower(),
            }
        )

        html = super().render(name, value, attrs, renderer)

        if cloudflare_images.is_configured():
            preview_url = ""
            if value:
                with contextlib.suppress(Exception):
                    preview_url = cloudflare_images.get_image_url(
                        value, width=200, height=200
                    )

            upload_button = format_html(
                '<button type="button" class="button cloudflare-upload-btn" data-target="{}">Upload Image</button>',
                attrs.get("id", name),
            )

            preview_html = format_html(
                '<div class="cloudflare-image-preview" data-target="{}"><img src="{}" style="max-width: 200px; max-height: 200px;" /></div>',
                attrs.get("id", name),
                preview_url,
            )

            html = format_html(
                '{}<div class="cloudflare-image-controls">{}{}</div>',
                html,
                upload_button,
                preview_html,
            )

        return html


class CloudflareImageField(blocks.CharBlock):
    """Field for storing Cloudflare Images IDs."""

    def __init__(self, required=True, help_text=None, **kwargs):
        """Initialize the CloudflareImageField."""
        if help_text is None:
            help_text = "Enter a Cloudflare Images ID or upload a new image"

        super().__init__(
            required=required,
            help_text=help_text,
            widget=CloudflareImageChooserWidget(),
            **kwargs,
        )

    def clean(self, value):
        """Validate that the image ID exists in Cloudflare Images."""
        cleaned_value = super().clean(value)

        if cleaned_value and cloudflare_images.is_configured():
            try:
                # Verify the image exists
                cloudflare_images.get_image_details(cleaned_value)
            except Exception:
                from wagtail.blocks import ValidationError

                msg = f"Image ID '{cleaned_value}' not found in Cloudflare Images"
                raise ValidationError(msg)

        return cleaned_value


class CloudflareImageBlock(blocks.StructBlock):
    """
    Image block that uses Cloudflare Images for optimized delivery.

    This block stores the Cloudflare Images ID and provides various
    display and transformation options.
    """

    image_id = CloudflareImageField(
        required=True, help_text="Cloudflare Images ID for the image"
    )
    alt_text = blocks.CharBlock(
        required=False, max_length=200, help_text="Alternative text for accessibility"
    )
    caption = blocks.CharBlock(
        required=False, max_length=300, help_text="Optional caption for the image"
    )
    alignment = blocks.ChoiceBlock(
        choices=[
            ("left", "Left aligned"),
            ("center", "Center aligned"),
            ("right", "Right aligned"),
            ("full", "Full width"),
        ],
        default="center",
        help_text="How to align the image",
    )
    size = blocks.ChoiceBlock(
        choices=[
            ("small", "Small (400px)"),
            ("medium", "Medium (600px)"),
            ("large", "Large (800px)"),
            ("xl", "Extra Large (1000px)"),
            ("full", "Full width"),
        ],
        default="medium",
        help_text="Image display size",
    )
    variant = blocks.ChoiceBlock(
        choices=[
            ("public", "Standard quality"),
            ("compressed", "Compressed (faster loading)"),
            ("high_quality", "High quality"),
        ],
        default="public",
        help_text="Image quality variant",
    )
    lazy_loading = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Enable lazy loading for better performance",
    )
    enable_zoom = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Allow users to click to zoom the image",
    )

    class Meta:
        icon = "image"
        label = "Cloudflare Image"
        help_text = "An image served through Cloudflare Images CDN"
        template = "public_site/blocks/cloudflare_image_block.html"

    def get_context(self, value, parent_context=None):
        """Add image URLs to the template context."""
        context = super().get_context(value, parent_context)

        if value.get("image_id") and cloudflare_images.is_configured():
            image_id = value["image_id"]
            variant = value.get("variant", "public")
            size = value.get("size", "medium")

            # Size mappings
            size_map = {
                "small": {"width": 400},
                "medium": {"width": 600},
                "large": {"width": 800},
                "xl": {"width": 1000},
                "full": {},  # No size constraints for full width
            }

            transforms = size_map.get(size, {})

            # Generate URLs for different formats
            context.update(
                {
                    "image_url": cloudflare_images.get_image_url(
                        image_id, variant=variant, **transforms
                    ),
                    "image_url_webp": cloudflare_images.get_image_url(
                        image_id, variant=variant, format="webp", **transforms
                    ),
                    "image_url_avif": cloudflare_images.get_image_url(
                        image_id, variant=variant, format="avif", **transforms
                    ),
                    "thumbnail_url": cloudflare_images.get_image_url(
                        image_id, variant=variant, width=300, height=200
                    ),
                    "configured": True,
                }
            )

            # Generate responsive image URLs
            if size != "full":
                base_width = transforms.get("width", 600)
                context["responsive_urls"] = {
                    "1x": cloudflare_images.get_image_url(
                        image_id, variant=variant, width=base_width
                    ),
                    "2x": cloudflare_images.get_image_url(
                        image_id, variant=variant, width=base_width * 2
                    ),
                }
        else:
            context.update(
                {
                    "image_url": None,
                    "configured": False,
                }
            )

        return context


class CloudflareGalleryBlock(blocks.StructBlock):
    """
    Gallery block for displaying multiple Cloudflare Images.
    """

    title = blocks.CharBlock(
        required=False, max_length=100, help_text="Optional title for the gallery"
    )
    images = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("image_id", CloudflareImageField(help_text="Cloudflare Images ID")),
                (
                    "caption",
                    blocks.CharBlock(
                        required=False, max_length=200, help_text="Image caption"
                    ),
                ),
                (
                    "alt_text",
                    blocks.CharBlock(
                        required=False,
                        max_length=200,
                        help_text="Alt text for accessibility",
                    ),
                ),
            ]
        ),
        min_num=1,
        max_num=12,
        help_text="Add images to the gallery",
    )
    layout = blocks.ChoiceBlock(
        choices=[
            ("grid", "Grid layout"),
            ("masonry", "Masonry layout"),
            ("carousel", "Carousel/slider"),
            ("lightbox", "Lightbox grid"),
        ],
        default="grid",
        help_text="Gallery layout style",
    )
    columns = blocks.ChoiceBlock(
        choices=[
            ("2", "2 columns"),
            ("3", "3 columns"),
            ("4", "4 columns"),
            ("auto", "Auto (responsive)"),
        ],
        default="3",
        help_text="Number of columns (for grid layout)",
    )
    variant = blocks.ChoiceBlock(
        choices=[
            ("public", "Standard quality"),
            ("compressed", "Compressed"),
        ],
        default="public",
        help_text="Image quality for gallery thumbnails",
    )

    class Meta:
        icon = "grip"
        label = "Image Gallery"
        help_text = "Gallery of Cloudflare Images"
        template = "public_site/blocks/cloudflare_gallery_block.html"

    def get_context(self, value, parent_context=None):
        """Generate URLs for all gallery images."""
        context = super().get_context(value, parent_context)

        if cloudflare_images.is_configured():
            variant = value.get("variant", "public")
            processed_images = []

            for image_data in value.get("images", []):
                image_id = image_data.get("image_id")
                if image_id:
                    processed_images.append(
                        {
                            "id": image_id,
                            "caption": image_data.get("caption", ""),
                            "alt_text": image_data.get("alt_text", ""),
                            "thumbnail_url": cloudflare_images.get_image_url(
                                image_id, variant=variant, width=400, height=300
                            ),
                            "full_url": cloudflare_images.get_image_url(
                                image_id, variant=variant, width=1200
                            ),
                            "original_url": cloudflare_images.get_image_url(
                                image_id, variant=variant
                            ),
                        }
                    )

            context["processed_images"] = processed_images
            context["configured"] = True
        else:
            context["configured"] = False

        return context


class CloudflareHeroImageBlock(blocks.StructBlock):
    """
    Hero image block optimized for large banner images.
    """

    image_id = CloudflareImageField(
        required=True, help_text="Cloudflare Images ID for the hero image"
    )
    alt_text = blocks.CharBlock(
        required=False, max_length=200, help_text="Alternative text for accessibility"
    )
    overlay_text = blocks.CharBlock(
        required=False, max_length=200, help_text="Text to overlay on the image"
    )
    overlay_position = blocks.ChoiceBlock(
        choices=[
            ("center", "Center"),
            ("top-left", "Top Left"),
            ("top-right", "Top Right"),
            ("bottom-left", "Bottom Left"),
            ("bottom-right", "Bottom Right"),
        ],
        default="center",
        help_text="Position of overlay text",
    )
    height = blocks.ChoiceBlock(
        choices=[
            ("small", "Small (300px)"),
            ("medium", "Medium (500px)"),
            ("large", "Large (700px)"),
            ("viewport", "Full viewport height"),
        ],
        default="large",
        help_text="Height of the hero image",
    )
    enable_parallax = blocks.BooleanBlock(
        required=False, default=False, help_text="Enable parallax scrolling effect"
    )

    class Meta:
        icon = "image"
        label = "Hero Image"
        help_text = "Large banner image with optional overlay text"
        template = "public_site/blocks/cloudflare_hero_block.html"

    def get_context(self, value, parent_context=None):
        """Generate optimized URLs for hero image."""
        context = super().get_context(value, parent_context)

        if value.get("image_id") and cloudflare_images.is_configured():
            image_id = value["image_id"]

            # Generate URLs for different screen sizes
            context.update(
                {
                    "mobile_url": cloudflare_images.get_image_url(
                        image_id, width=768, quality=80
                    ),
                    "tablet_url": cloudflare_images.get_image_url(
                        image_id, width=1024, quality=85
                    ),
                    "desktop_url": cloudflare_images.get_image_url(
                        image_id, width=1920, quality=90
                    ),
                    "retina_url": cloudflare_images.get_image_url(
                        image_id, width=3840, quality=85
                    ),
                    "webp_url": cloudflare_images.get_image_url(
                        image_id, width=1920, format="webp", quality=80
                    ),
                    "configured": True,
                }
            )
        else:
            context["configured"] = False

        return context
