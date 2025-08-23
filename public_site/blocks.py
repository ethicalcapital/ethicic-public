"""
Simplified StreamField blocks for clean blog content creation.
Removed AI features to focus on essential CMS functionality.
"""

from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock

# ============================================================================
# BASIC STREAMFIELD BLOCKS
# ============================================================================


class HeadingBlock(blocks.StructBlock):
    """Heading block with size options."""

    heading_text = blocks.CharBlock(classname="title")
    size = blocks.ChoiceBlock(
        choices=[
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        default="h2",
    )

    class Meta:
        template = "blocks/heading_block.html"
        icon = "title"
        label = "Heading"


class ParagraphBlock(blocks.RichTextBlock):
    """Rich text paragraph block."""

    class Meta:
        template = "blocks/paragraph_block.html"
        icon = "pilcrow"
        label = "Paragraph"


class RichTextBlock(blocks.RichTextBlock):
    """Standard rich text block."""

    class Meta:
        template = "blocks/rich_text_block.html"
        icon = "pilcrow"
        label = "Rich Text"


class ImageBlock(blocks.StructBlock):
    """Image block with caption and alignment."""

    image = ImageChooserBlock()
    caption = blocks.CharBlock(required=False)
    alignment = blocks.ChoiceBlock(
        choices=[
            ("left", "Left"),
            ("right", "Right"),
            ("center", "Center"),
            ("full", "Full Width"),
        ],
        default="center",
    )

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"
        label = "Image"


class EmbedVideoBlock(EmbedBlock):
    """Video embed block."""

    class Meta:
        template = "public_site/blocks/video_block.html"
        icon = "media"
        label = "Video"


class YouTubeVideoBlock(blocks.StructBlock):
    """Enhanced YouTube video block with additional options."""
    
    youtube_url = blocks.URLBlock(
        help_text="Enter YouTube video URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID or https://youtu.be/VIDEO_ID)"
    )
    title = blocks.CharBlock(
        required=False,
        help_text="Optional title/caption for the video"
    )
    start_time = blocks.IntegerBlock(
        required=False,
        help_text="Start time in seconds (optional)"
    )
    autoplay = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Enable autoplay (not recommended for accessibility)"
    )
    
    class Meta:
        template = "public_site/blocks/youtube_video_block.html"
        icon = "media"
        label = "YouTube Video"


class DocumentBlock(blocks.StructBlock):
    """Document download block."""

    document = DocumentChooserBlock()
    title = blocks.CharBlock(required=False)

    class Meta:
        template = "blocks/document_block.html"
        icon = "doc-full"
        label = "Document"


class QuoteBlock(blocks.StructBlock):
    """Quote/testimonial block."""

    quote = blocks.TextBlock()
    author = blocks.CharBlock(required=False)
    source = blocks.CharBlock(required=False)

    class Meta:
        template = "blocks/quote_block.html"
        icon = "openquote"
        label = "Quote"


class CalloutBlock(blocks.StructBlock):
    """Callout/highlight block."""

    title = blocks.CharBlock(required=False)
    content = blocks.RichTextBlock()
    style = blocks.ChoiceBlock(
        choices=[
            ("info", "Information"),
            ("warning", "Warning"),
            ("success", "Success"),
            ("error", "Error"),
        ],
        default="info",
    )

    class Meta:
        template = "blocks/callout_block.html"
        icon = "help"
        label = "Callout"


class KeyStatisticBlock(blocks.StructBlock):
    """Simple statistic block for highlighting key data points."""

    value = blocks.CharBlock(
        max_length=50, help_text="The statistic value (e.g., '12.4%', '$1.2M', '3.8x')"
    )
    label = blocks.CharBlock(
        max_length=100,
        help_text="Statistic label (e.g., 'Annual Return', 'Market Cap')",
    )
    description = blocks.TextBlock(
        required=False, help_text="Optional description or context for this statistic"
    )

    class Meta:
        template = "blocks/key_statistic_simple.html"
        icon = "snippet"
        label = "Key Statistic"


class SimpleTableBlock(TableBlock):
    """Table block for data presentation."""

    class Meta:
        template = "public_site/blocks/table_block.html"
        icon = "table"
        label = "Table"


class DividerBlock(blocks.StaticBlock):
    """Horizontal divider."""

    class Meta:
        template = "public_site/blocks/divider_block.html"
        icon = "horizontalrule"
        label = "Divider"
        admin_text = "Horizontal line separator"


# ============================================================================
# STREAMFIELD DEFINITION
# ============================================================================


class BlogStreamField(StreamField):
    """Simplified StreamField for clean blog content creation."""

    def __init__(self, *args, **kwargs):
        block_types = [
            ("heading", HeadingBlock()),
            ("paragraph", ParagraphBlock()),
            ("rich_text", RichTextBlock()),
            ("image", ImageBlock()),
            ("video", EmbedVideoBlock()),
            ("youtube_video", YouTubeVideoBlock()),
            ("document", DocumentBlock()),
            ("quote", QuoteBlock()),
            ("callout", CalloutBlock()),
            ("key_statistic", KeyStatisticBlock()),
            ("table", SimpleTableBlock()),
            ("divider", DividerBlock()),
        ]

        kwargs.setdefault("block_types", block_types)
        super().__init__(*args, **kwargs)
