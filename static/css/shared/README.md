# Garden UI Shared Design Tokens

This directory contains shared design tokens and component base classes that enable visual consistency between the Garden Financial Platform and the Ethicic Public Site.

## Structure

- `garden-brand-tokens.css` - Core design tokens (colors, spacing, typography variables)
- `garden-component-base.css` - Base component classes (buttons, panels, inputs)

## Usage in Garden Platform

To use these shared tokens in the Garden platform:

1. **Import the tokens in your main CSS file:**
```css
@import url('/path/to/shared/garden-brand-tokens.css');
@import url('/path/to/shared/garden-component-base.css');
```

2. **Use the design tokens in your styles:**
```css
.my-button {
  background-color: var(--garden-brand-purple);
  padding: var(--garden-space-2) var(--garden-space-4);
  font-family: var(--garden-brand-font-sans);
}
```

3. **Extend the base components:**
```css
.garden-action.custom-variant {
  background-color: var(--garden-brand-teal);
  /* Your custom styles */
}
```

## Design Token Reference

### Colors
- `--garden-brand-purple`: Primary brand purple (#581c87)
- `--garden-brand-teal`: Secondary brand teal (#14b8a6)
- `--garden-brand-gray-[50-900]`: Gray scale for backgrounds and text

### Spacing
- `--garden-space-[1-32]`: Consistent spacing scale (4px to 128px)

### Typography
- `--garden-brand-font-sans`: Primary font (Outfit)
- `--garden-brand-font-heading`: Display font (Bebas Neue)
- `--garden-brand-text-[xs-5xl]`: Font size scale

### Components
- `.garden-action`: Base button class with primary/secondary variants
- `.garden-panel`: Base container/card class
- `.garden-input`: Base form input class

## Principles

1. **Additive Only**: These files should only add new tokens, never break existing functionality
2. **No Implementation Details**: Keep site-specific styles in their respective codebases
3. **Semantic Naming**: Use clear, purpose-driven names for all tokens
4. **Dark Mode Support**: Include appropriate theme adjustments

## Versioning

Always use cache-busting query parameters when importing these files:
```html
<link rel="stylesheet" href="{% static 'css/shared/garden-brand-tokens.css' %}?v=1" />
```

## Contributing

When adding new tokens:
1. Ensure they're truly shared between both platforms
2. Document the token's purpose
3. Test in both light and dark modes
4. Update this README with any new patterns