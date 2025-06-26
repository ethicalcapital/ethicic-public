"""
Blog template filters for enhancing blog display with extracted statistics and visual elements.
Implements the monospace info-dense aesthetic enhancements from WIP/blog.md guidance.
"""

import re

from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def extract_key_stats(content):
    """Extract percentages, dollar amounts, and key metrics from blog content.

    Returns a dictionary with categorized statistics that can be used for
    data callouts and visual enhancements.
    """
    if not content:
        return {}

    # Convert content to plain text for pattern matching
    text_content = strip_tags(str(content))

    patterns = {
        'percentages': r'([+-]?\d+\.?\d*%)',
        'dollar_amounts': r'\$(\d+(?:,\d{3})*(?:\.\d{2})?[BMK]?)',
        'returns': r'([+-]?\d+\.?\d*%)\s*(?:return|performance|gain|loss)',
        'years': r'(20\d{2})',
        'positions': r'(\d+\.?\d*%)\s*(?:of|position|weight|allocation|holding)',
        'ratios': r'(\d+\.?\d*)\s*(?:ratio|multiple|times|x)',
        'basis_points': r'(\d+)\s*(?:basis points|bps)',
        'market_cap': r'\$(\d+(?:\.\d+)?[BMT]?)\s*(?:market cap|billion|million)',
    }

    stats = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        # Take top 4 matches and clean them up
        stats[key] = [match.strip() for match in matches[:4]]

    return stats


@register.filter
def highlight_stats(content):
    """Highlight key statistics in blog content with monospace styling.

    Wraps percentages, dollar amounts, and other key metrics in
    highlighting spans for visual emphasis.
    """
    if not content:
        return content

    # Patterns to highlight
    highlight_patterns = [
        (r'([+-]?\d+\.?\d*%)', r'<span class="stat-highlight">\1</span>'),
        (r'(\$\d+(?:,\d{3})*(?:\.\d{2})?[BMK]?)', r'<span class="stat-highlight">\1</span>'),
        (r'(\d+\.?\d*)\s*(basis points|bps)', r'<span class="stat-highlight">\1 \2</span>'),
    ]

    highlighted_content = str(content)
    for pattern, replacement in highlight_patterns:
        highlighted_content = re.sub(pattern, replacement, highlighted_content, flags=re.IGNORECASE)

    return mark_safe(highlighted_content)


@register.filter
def generate_data_header(post):
    """Generate data header with key metrics for blog post.

    Extracts the top 4 most relevant statistics from the post
    and formats them for the data header display.
    """
    if not post:
        return []

    # Extract content from both new StreamField and legacy body field
    content = ""
    if hasattr(post, 'content') and post.content:
        content = str(post.content)
    elif hasattr(post, 'body') and post.body:
        content = str(post.body)

    stats = extract_key_stats(content)

    # Prioritize different types of stats
    data_points = []

    # Portfolio positions and weights
    if stats.get('positions'):
        for pos in stats['positions'][:2]:
            data_points.append({
                'value': pos,
                'label': 'PORTFOLIO WEIGHT'
            })

    # Performance returns
    if stats.get('returns'):
        for ret in stats['returns'][:2]:
            data_points.append({
                'value': ret,
                'label': 'PERFORMANCE'
            })

    # General percentages
    if stats.get('percentages') and len(data_points) < 4:
        for pct in stats['percentages'][:2]:
            if pct not in [dp['value'] for dp in data_points]:  # Avoid duplicates
                data_points.append({
                    'value': pct,
                    'label': 'KEY METRIC'
                })

    # Dollar amounts
    if stats.get('dollar_amounts') and len(data_points) < 4:
        for amt in stats['dollar_amounts'][:1]:
            data_points.append({
                'value': f'${amt}',
                'label': 'VALUE'
            })

    return data_points[:4]  # Maximum 4 data points for header


@register.filter
def generate_post_visual(post):
    """Generate appropriate visual based on post content type and data."""
    if not post:
        return ""

    post_type = extract_post_type(post)
    content = ""

    if hasattr(post, 'content') and post.content:
        content = str(post.content)
    elif hasattr(post, 'body') and post.body:
        content = str(post.body)

    if post_type == 'performance':
        return generate_performance_visual(content)
    if post_type == 'holdings':
        return generate_holdings_visual(content)
    return generate_general_visual(content)


def generate_performance_visual(content):
    """Create performance-focused ASCII visual."""
    stats = extract_key_stats(content)

    if stats.get('returns'):
        returns = stats['returns'][:2]
        try:
            values = [float(re.search(r'[\d.]+', ret).group()) for ret in returns if re.search(r'[\d.]+', ret)]
            if len(values) >= 2:
                portfolio_return = values[0]
                benchmark_return = values[1] if len(values) > 1 else 0

                visual = f"""PERFORMANCE COMPARISON
┌─────────────────────────────────────┐
│  Portfolio: {portfolio_return:+.2f}%   Benchmark: {benchmark_return:+.2f}%  │
│  {'▲' * 25 if portfolio_return > benchmark_return else '▽' * 25}  │
│  Outperformance vs Market Index     │
└─────────────────────────────────────┘"""
                return mark_safe(f'<pre class="ascii-visual">{visual}</pre>')
        except (ValueError, AttributeError):
            pass

    return ""


def generate_holdings_visual(content):
    """Create holdings-focused ASCII visual."""
    stats = extract_key_stats(content)

    if stats.get('positions'):
        positions = stats['positions'][:4]
        try:
            visual_lines = ["PORTFOLIO ALLOCATION", "═" * 30]

            for pos in positions:
                val = float(re.search(r'[\d.]+', pos).group())
                bar_length = int(val / 2)  # Scale for display
                bar = "█" * bar_length
                visual_lines.append(f"Position Weight  {bar:<15} {val:>6.1f}%")

            return mark_safe('<pre class="ascii-visual">\n' + '\n'.join(visual_lines) + '\n</pre>')
        except (ValueError, AttributeError):
            pass

    return ""


def generate_general_visual(content):
    """Create general visual for posts with key statistics."""
    stats = extract_key_stats(content)

    # Create a summary box with key stats
    visual_lines = ["KEY METRICS SUMMARY", "─" * 25]

    if stats.get('percentages'):
        for pct in stats['percentages'][:3]:
            visual_lines.append(f"• {pct} Key Percentage")

    if stats.get('dollar_amounts'):
        for amt in stats['dollar_amounts'][:2]:
            visual_lines.append(f"• ${amt} Value Reference")

    if len(visual_lines) > 2:  # Only show if we have actual stats
        return mark_safe('<pre class="ascii-visual">\n' + '\n'.join(visual_lines) + '\n</pre>')

    return ""


@register.filter
def generate_ascii_chart(value_list, chart_type="bar"):
    """Generate ASCII charts for visual representation of data.

    Creates monospace ASCII charts that fit the terminal aesthetic.
    """
    if not value_list or not isinstance(value_list, list | tuple):
        return ""

    if chart_type == "bar":
        return generate_ascii_bar_chart(value_list)
    if chart_type == "performance":
        return generate_ascii_performance_chart(value_list)
    return ""


def generate_ascii_bar_chart(data):
    """Generate ASCII bar chart."""
    if not data:
        return ""

    # Extract numeric values
    values = []
    labels = []

    for item in data:
        if isinstance(item, dict):
            val = item.get('value', 0)
            label = item.get('label', 'Item')
        else:
            val = float(re.search(r'[\d.]+', str(item)).group()) if re.search(r'[\d.]+', str(item)) else 0
            label = str(item)

        values.append(val)
        labels.append(label[:15])  # Truncate long labels

    if not values:
        return ""

    max_val = max(values)
    chart_width = 30

    chart_lines = []
    chart_lines.append("ALLOCATION BREAKDOWN")
    chart_lines.append("═" * (chart_width + 20))

    for _i, (val, label) in enumerate(zip(values, labels, strict=False)):
        bar_length = int((val / max_val) * chart_width) if max_val > 0 else 0
        bar = "█" * bar_length
        padding = " " * (chart_width - bar_length)
        chart_lines.append(f"{label:<15} {bar}{padding} {val:>6.1f}%")

    return mark_safe('<pre class="ascii-chart">\n' + '\n'.join(chart_lines) + '\n</pre>')


def generate_ascii_performance_chart(data):
    """Generate ASCII performance chart."""
    chart_lines = []
    chart_lines.append("QUARTERLY PERFORMANCE")
    chart_lines.append("┌─────────────────────────────────────┐")

    if data and len(data) >= 2:
        portfolio_val = data[0] if isinstance(data[0], int | float) else float(re.search(r'[\d.]+', str(data[0])).group())
        benchmark_val = data[1] if isinstance(data[1], int | float) else float(re.search(r'[\d.]+', str(data[1])).group())

        chart_lines.append(f"│  Portfolio: {portfolio_val:+.2f}%   Benchmark: {benchmark_val:+.2f}%   │")

        # Visual comparison
        if portfolio_val > benchmark_val:
            symbols = "▲" * 25 + "▽" * 6
        else:
            symbols = "▽" * 25 + "▲" * 6

        chart_lines.append(f"│  {symbols} │")
        chart_lines.append("│  Performance vs. Benchmark          │")
    else:
        chart_lines.append("│  Insufficient data for comparison  │")

    chart_lines.append("└─────────────────────────────────────┘")

    return mark_safe('<pre class="ascii-chart">\n' + '\n'.join(chart_lines) + '\n</pre>')


@register.filter
def extract_post_type(post):
    """Determine the type of blog post based on content analysis.

    Returns: 'performance', 'holdings', 'analysis', or 'general'
    """
    if not post:
        return 'general'

    # Extract content
    content = ""
    title = getattr(post, 'title', '').lower()

    if hasattr(post, 'content') and post.content:
        content = str(post.content).lower()
    elif hasattr(post, 'body') and post.body:
        content = str(post.body).lower()

    # Check for performance-related content
    performance_keywords = ['performance', 'return', 'quarterly', 'annual', 'benchmark', 'outperform']
    if any(keyword in title or keyword in content for keyword in performance_keywords):
        return 'performance'

    # Check for holdings/position analysis
    holdings_keywords = ['holding', 'position', 'portfolio', 'allocation', 'weight']
    if any(keyword in title or keyword in content for keyword in holdings_keywords):
        return 'holdings'

    # Check for company/security analysis
    analysis_keywords = ['analysis', 'review', 'deep dive', 'company', 'stock', 'security']
    if any(keyword in title or keyword in content for keyword in analysis_keywords):
        return 'analysis'

    return 'general'


@register.filter
def format_inline_stat(value, context=""):
    """Format an inline statistic with proper styling and context."""
    if not value:
        return ""

    return mark_safe(
        f'<div class="inline-stat-callout">'
        f'<span class="stat-highlight">{value}</span>'
        f'<span class="stat-context">{context}</span>'
        f'</div>'
    )


@register.filter
def split(value, delimiter=","):
    """Split a string by delimiter and return a list.

    Usage: {{ "apple,banana,cherry"|split:"," }}
    """
    if not value:
        return []
    return str(value).split(delimiter)


@register.filter
def trim(value):
    """Remove leading and trailing whitespace from a string.

    Usage: {{ "  text  "|trim }}
    """
    if not value:
        return ""
    return str(value).strip()


@register.filter
def hash(value):
    """Generate a simple hash for use as unique ID in templates.

    Usage: {{ value|hash }}
    """
    if not value:
        return "0"
    return str(abs(hash(str(value))))[:8]  # Take first 8 digits for reasonable ID length


@register.filter
def select_key_statistics(content):
    """Extract key statistic blocks from StreamField content.

    Usage: {{ page.content|select_key_statistics }}
    """
    if not content:
        return []

    key_stats = []
    for block in content:
        if hasattr(block, 'block_type') and block.block_type in ['key_statistic', 'ai_statistic']:
            key_stats.append(block)

    return key_stats

# Keep old filter name for backward compatibility
@register.filter
def select_ai_statistics(content):
    """Legacy filter name - use select_key_statistics instead."""
    return select_key_statistics(content)


@register.filter
def blog_stats_summary(blog_index_page):
    """Generate summary statistics for the blog index page."""
    if not blog_index_page:
        return {}

    try:
        posts = blog_index_page.get_posts()
        total_posts = posts.count()

        # Get publication date range
        first_post = posts.order_by('first_published_at').first()
        latest_post = posts.order_by('-first_published_at').first()

        since_year = first_post.first_published_at.year if first_post else None

        # Count featured posts
        featured_count = posts.filter(featured=True).count()

        # Get unique tags count
        all_tags = blog_index_page.get_all_tags()
        tags_count = len(all_tags)

        return {
            'total_posts': total_posts,
            'featured_count': featured_count,
            'tags_count': tags_count,
            'since_year': since_year,
            'latest_date': latest_post.first_published_at if latest_post else None,
        }
    except Exception:
        return {
            'total_posts': 0,
            'featured_count': 0,
            'tags_count': 0,
            'since_year': None,
            'latest_date': None,
        }
