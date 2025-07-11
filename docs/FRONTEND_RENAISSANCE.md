# Django Frontend Renaissance Implementation

This document outlines the implementation of modern frontend techniques in the Ethical Capital public site, based on the Django Frontend Renaissance principles.

## Stack Overview

### Core Technologies
- **HTMX** - Server-driven interactivity without complex JavaScript
- **Alpine.js** - Lightweight reactive framework for client-side state
- **Django Templates** - Server-side rendering with Django's template engine
- **Garden UI** - Our custom design system with CSS variables

## Implementation Guide

### 1. HTMX Integration

HTMX is loaded in the base template and provides server-driven interactivity:

```html
<!-- In base.html -->
<script src="https://unpkg.com/htmx.org@1.9.11"></script>
```

#### Live Search Example
```html
<input type="text"
       hx-get="/search/live/"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#search-results"
       hx-indicator="#search-spinner">
```

#### Form Submission
```html
<form hx-post="/api/contact/"
      hx-target="#form-result"
      hx-indicator="#submit-spinner">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### 2. Alpine.js Components

Alpine.js provides reactive client-side behavior with minimal JavaScript:

#### Theme Toggle
```html
<button x-data="{
    isDark: localStorage.getItem('theme') === 'dark',
    toggle() {
        this.isDark = !this.isDark;
        const theme = this.isDark ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
}"
@click="toggle()"
aria-label="Toggle theme">
    <span x-text="isDark ? '☾' : '☀'"></span>
</button>
```

#### Dropdown Menu
```html
<div x-data="{ open: false }"
     @click.outside="open = false"
     @keydown.escape="open = false">
    <button @click="open = !open">Menu</button>
    <div x-show="open" x-transition>
        <!-- menu items -->
    </div>
</div>
```

### 3. Partial Templates

Create reusable partial templates for HTMX responses:

```django
# views.py
def site_search_live(request):
    query = request.GET.get('q', '')
    results = Page.objects.live().search(query)[:5]

    if request.headers.get('HX-Request'):
        # Return partial for HTMX
        return render(request, 'partials/search_results.html', {
            'results': results
        })
    else:
        # Full page for non-HTMX
        return redirect(f'/search/?q={query}')
```

### 4. Progressive Enhancement

The site works without JavaScript and progressively enhances with HTMX/Alpine:

```html
<!-- Search form works with or without HTMX -->
<form method="get" action="/search/">
    <input type="text"
           name="q"
           hx-get="/search/live/"
           hx-trigger="keyup changed delay:300ms">
    <button type="submit">Search</button>
</form>
```

## Benefits

1. **Reduced Complexity** - No build process, no bundlers, no npm
2. **Better Performance** - Less JavaScript to parse and execute
3. **SEO Friendly** - Server-side rendering by default
4. **Maintainable** - Clear separation of concerns
5. **Progressive** - Works without JavaScript, enhances with it

## Best Practices

1. **Use HTMX for**:
   - Form submissions
   - Partial page updates
   - Infinite scroll
   - Live search
   - Polling for updates

2. **Use Alpine.js for**:
   - Client-side state (dropdowns, modals)
   - Form validation feedback
   - Interactive UI elements
   - Theme switching

3. **Keep JavaScript minimal**:
   - Prefer HTMX over custom AJAX
   - Use Alpine.js instead of jQuery
   - Let the server handle business logic

4. **Optimize for performance**:
   - Use `hx-trigger="once"` for one-time loads
   - Add debouncing with `delay:` modifier
   - Use indicators for loading states
   - Cache partial templates

## Migration Strategy

1. **Phase 1**: Add HTMX and Alpine.js to base template ✓
2. **Phase 2**: Convert interactive elements to Alpine.js ✓
3. **Phase 3**: Add HTMX to forms and search ✓
4. **Phase 4**: Create partial views for dynamic content
5. **Phase 5**: Remove unnecessary JavaScript

## Examples

See `/templates/public_site/examples/htmx_faq_example.html` for working examples of:
- FAQ accordion with lazy loading
- Form validation with HTMX
- Infinite scroll pattern
- Loading states and indicators

### Additional Components

**Live Statistics Widget** (`/templates/public_site/components/live_stats.html`):
- Polls `/api/live-stats/` every 30 seconds
- Shows loading states with skeleton screens
- Updates timestamp on each refresh

**Notification Bell** (`/templates/public_site/components/notification_bell.html`):
- Polls `/api/notifications/count/` every 60 seconds for badge count
- Polls `/api/notifications/` every 30 seconds when dropdown is open
- Supports marking all as read with HTMX POST

**Newsletter Form** (`/templates/public_site/components/newsletter_form_htmx.html`):
- HTMX-powered newsletter signup
- Alpine.js for client-side state
- Shows success/error messages inline
