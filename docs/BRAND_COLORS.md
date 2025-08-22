# Ethical Capital Brand Colors

Last Updated: 2025-01-26

## Primary Brand Colors

### Purple (Main Brand)
- **Primary**: `#581c87` (purple-700) - Main brand purple
- **Light**: `#6b46c1` (purple-600) - Hover states
- **Dark**: `#1f0322` - Very dark purple for accents
- **Pale**: `rgb(88 28 135 / 0.15)` - 15% opacity for backgrounds

### Teal (CTA/Secondary)
- **Primary**: `#00ABB9` - Main CTA color
- **Hover**: `#00c2d1` - Lighter on hover
- **Active**: `#009aa7` - Darker when pressed

## Usage Guidelines

### Purple Usage
- **Headers/Hero**: Use primary purple (#581c87) or Tailwind's purple-700
- **Backgrounds**: Use gradients with purple-900, purple-800
- **Dark Accents**: Use the very dark purple (#1f0322) sparingly

### Teal Usage
- **Primary CTAs**: "Schedule Consultation", "Get Started" buttons
- **Secondary buttons**: Use with white text for good contrast
- **Accent elements**: Links, highlights on purple backgrounds

## CSS Variables

### In Tailwind Config
- `ec-purple` (DEFAULT, light, dark, pale)
- `ec-teal` (DEFAULT, hover, active)

### In CSS Files
- `--ec-purple-primary`: #581c87
- `--ec-purple-light`: #6b46c1
- `--ec-purple-dark`: #1f0322
- `--ec-teal-primary`: #00ABB9
- `--ec-teal-light`: #00c2d1
- `--ec-teal-dark`: #009aa7
- `--color-cta`: #00ABB9

## Tailwind Classes
- Purple: `bg-purple-700`, `bg-purple-800`, `bg-purple-900`
- Teal: `bg-ec-teal`, `bg-ec-teal-hover`, `bg-ec-teal-active`
- Custom: `bg-ec-purple`, `bg-ec-purple-light`, `bg-ec-purple-dark`

## Notes
- The site previously mixed different color values, now standardized
- Emergency CSS may override some colors for visibility
- Always test color contrast for WCAG AA compliance