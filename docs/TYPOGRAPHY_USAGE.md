# Typography Usage Guide

## Centralized Font Control

All fonts are centrally controlled through `/static/css/typography-config.css`. This ensures consistent typography across the entire site and makes font changes easy.

## Font Families

### CSS Variables (Preferred)
- `--font-family-heading`: Bebas Neue (for all headings)
- `--font-family-body`: Raleway (for body text)
- `--font-family-ui`: Raleway (for UI elements)

### Tailwind Classes
- `font-heading`: Uses var(--font-family-heading)
- `font-body`: Uses var(--font-family-body)
- `font-ui`: Uses var(--font-family-ui)
- `font-serif`: Maps to Bebas Neue (legacy)
- `font-sans`: Maps to Raleway (legacy)

## Usage Examples

### Headings
```html
<!-- Preferred: Uses centralized CSS variable -->
<h1 class="font-heading text-4xl font-bold">Main Title</h1>
<h2 class="font-heading text-2xl font-semibold">Section Title</h2>

<!-- Legacy (still works) -->
<h1 class="font-serif text-4xl font-bold">Main Title</h1>
```

### Body Text
```html
<p class="font-body text-base">Regular paragraph text</p>
<p class="font-sans text-base">Also works (legacy)</p>
```

### UI Elements
```html
<button class="font-ui font-medium">Click Me</button>
```

## Changing Fonts Site-wide

To change any font across the entire site:

1. Edit `/static/css/typography-config.css`
2. Update the relevant CSS variable:
   ```css
   --font-family-heading: "New Font Name", fallback-font, sans-serif;
   ```
3. Rebuild CSS: `npm run build:css`

All elements using `font-heading`, `font-serif`, or any heading-specific classes will automatically use the new font.

## Panel Titles

The `.panel-title-ec` class automatically uses the heading font through:
```css
font-family: var(--font-family-heading);
```

No need to add additional font classes to panel titles.