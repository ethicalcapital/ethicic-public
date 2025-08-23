# YouTube Video Embedding for Wagtail Streamfields

This documentation describes the YouTube video embedding functionality added to the Wagtail Streamfield system for blog posts and content pages.

## Overview

Two video embedding options are now available in the Streamfield editor:

1. **Video Block** - General video embed block using Wagtail's built-in embed functionality (supports YouTube, Vimeo, and other platforms)
2. **YouTube Video Block** - Enhanced YouTube-specific block with additional controls and optimizations

## YouTube Video Block Features

### Input Fields
- **YouTube URL**: Accepts various YouTube URL formats
  - `https://www.youtube.com/watch?v=VIDEO_ID`
  - `https://youtu.be/VIDEO_ID`
  - `https://youtube.com/watch?v=VIDEO_ID`
  - `https://m.youtube.com/watch?v=VIDEO_ID`
- **Title**: Optional caption/title for the video
- **Start Time**: Optional start time in seconds
- **Autoplay**: Optional autoplay setting (not recommended for accessibility)

### Features
- **Responsive Design**: 16:9 aspect ratio that adapts to all screen sizes
- **Professional Styling**: Matches the site's Tailwind CSS design system
- **Loading States**: Shows loading spinner while video loads
- **Error Handling**: Displays appropriate error messages for failed video loads
- **Accessibility**: Proper ARIA labels, keyboard navigation support, and reduced motion support
- **Privacy Enhanced**: Uses privacy-enhanced YouTube embed mode
- **Clean Interface**: Minimal YouTube branding, no related videos at end

## Technical Implementation

### StreamField Blocks

```python
# In public_site/blocks.py
class YouTubeVideoBlock(blocks.StructBlock):
    """Enhanced YouTube video block with additional options."""
    
    youtube_url = blocks.URLBlock(
        help_text="Enter YouTube video URL"
    )
    title = blocks.CharBlock(required=False)
    start_time = blocks.IntegerBlock(required=False)
    autoplay = blocks.BooleanBlock(required=False, default=False)
```

### Template Tags

The implementation includes several helper functions in `public_site/templatetags/blog_filters.py`:

- `youtube_embed_url`: Converts YouTube URLs to embed format with parameters
- `extract_youtube_id`: Extracts video ID from various YouTube URL formats
- `youtube_thumbnail`: Gets YouTube thumbnail URL from video URL
- `is_youtube_url`: Validates if URL is from YouTube

### Template Structure

```html
<!-- Responsive 16:9 container -->
<div class="aspect-video w-full bg-slate-900 rounded-lg overflow-hidden shadow-lg border border-slate-600">
  <iframe
    src="{% youtube_embed_url value.youtube_url value.start_time value.autoplay %}"
    class="w-full h-full rounded-lg"
    allowfullscreen
    loading="lazy">
  </iframe>
</div>
```

## Usage Instructions

### For Content Editors

1. In the Wagtail admin, edit a blog post or content page
2. In the content StreamField, click "+" to add a block
3. Choose either:
   - **Video** - For general video embeds (any platform)
   - **YouTube Video** - For enhanced YouTube functionality

#### Using the YouTube Video Block:

1. Paste any YouTube video URL in the "YouTube URL" field
2. Optionally add a title/caption
3. Optionally set a start time in seconds (e.g., 30 for 30 seconds in)
4. Save and publish

### Supported URL Formats

The YouTube Video Block accepts these URL formats:
- Full YouTube URLs: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Short URLs: `https://youtu.be/dQw4w9WgXcQ`
- Mobile URLs: `https://m.youtube.com/watch?v=dQw4w9WgXcQ`
- Embed URLs: `https://www.youtube.com/embed/dQw4w9WgXcQ`

## Styling and Responsive Design

### CSS Classes Applied

- `.aspect-video`: Maintains 16:9 aspect ratio
- `.w-full`: Full width of container
- `.rounded-lg`: Professional rounded corners
- `.shadow-lg`: Subtle shadow for depth
- `.border-slate-600`: Professional border color

### Mobile Responsiveness

- Videos automatically scale to container width
- Maintains proper aspect ratio on all devices
- Touch-friendly controls on mobile devices
- Optimized loading for mobile connections

### Dark Mode Support

- Video containers adapt to dark/light theme
- Proper contrast maintained in all modes
- Loading states match theme colors

## Security and Performance

### Privacy Features
- Uses privacy-enhanced YouTube embed mode
- Minimal YouTube branding (`modestbranding=1`)
- No related videos shown at end (`rel=0`)
- Closed captions enabled by default (`cc_load_policy=1`)

### Performance Optimizations
- Lazy loading of video iframes
- Optimized embed parameters
- Loading states prevent layout shift
- Proper error handling for failed loads

### Accessibility Features
- Proper ARIA labels for screen readers
- Keyboard navigation support
- Reduced motion support for users with vestibular disorders
- Focus indicators for keyboard users
- Semantic HTML structure

## Error Handling

The implementation includes comprehensive error handling:

1. **Invalid URLs**: Shows placeholder with error message
2. **Failed Video Loads**: Displays "Video Load Error" message
3. **Missing URLs**: Shows "No YouTube Video Selected" placeholder
4. **Network Issues**: Graceful degradation with informative messages

## Testing

The YouTube URL parsing has been tested with various URL formats:

```python
# Test URLs that work correctly:
test_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ", 
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
]
```

## Migration Notes

The implementation includes database migrations to add the new block types to existing StreamFields. Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Future Enhancements

Potential improvements for future development:

1. **Video Thumbnails**: Show YouTube thumbnail in admin preview
2. **Playlist Support**: Support for YouTube playlist embeds
3. **Custom Players**: Option to use custom video players
4. **Analytics Integration**: Track video engagement metrics
5. **Content Warnings**: Add content warning system for videos

## Browser Compatibility

Tested and compatible with:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Support

For issues with video embedding:
1. Verify the YouTube URL is correct and video is publicly available
2. Check browser console for any JavaScript errors
3. Ensure video is not restricted by geographic location
4. Test with different YouTube URL formats