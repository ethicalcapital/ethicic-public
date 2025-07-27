/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './public_site/**/*.py',
  ],
  theme: {
    extend: {
      colors: {
        // Ethical Capital Brand Colors from Garden UI tokens
        'ec-purple': {
          DEFAULT: '#1f0322',  // Primary dark purple
          light: '#2a0430',    // Hover state
          pale: 'rgb(31 3 34 / 0.15)',  // Alpha variant
        },
        'ec-teal': {
          DEFAULT: '#4fbbba',  // CTA teal
          hover: '#5cc7c6',    // Hover state
          active: '#3fa8a7',   // Active state
        },
        // Semantic colors aligned with Garden UI
        primary: {
          DEFAULT: '#1f0322',
          hover: '#2a0430',
          foreground: '#ffffff',
        },
        surface: {
          DEFAULT: '#1a1a1a',
          variant: '#2a2a2a',
          foreground: '#f0f0f0',
        },
        background: {
          DEFAULT: '#121212',
          foreground: '#f0f0f0',
        },
        border: {
          DEFAULT: '#333333',
          variant: '#444444',
        },
        // Add semantic color mappings for utility classes
        'surface-foreground': '#f0f0f0',
        'primary-foreground': '#ffffff',
        'primary-hover': '#2a0430',
        // Status colors
        success: {
          DEFAULT: '#065d42',
          alpha: 'rgb(6 93 66 / 0.15)',
        },
        warning: {
          DEFAULT: '#7a4f05',
          alpha: 'rgb(122 79 5 / 0.15)',
        },
        error: {
          DEFAULT: '#8b2222',
          alpha: 'rgb(139 34 34 / 0.15)',
        },
        info: {
          DEFAULT: '#1d4ed8',
          alpha: 'rgb(29 78 216 / 0.15)',
        },
        // Text colors
        text: {
          primary: '#f0f0f0',
          secondary: '#b0b0b0',
          tertiary: '#a0a0a0',
          inverse: '#1a1a1a',
        },
        // Utility colors
        muted: '#b0b0b0',
        hover: '#222222',
        focus: '#2a2a2a',
        active: '#333333',
      },
      fontFamily: {
        'mono': ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
        'sans': ['var(--font-sans)', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'xs': ['var(--font-xs)', { lineHeight: 'var(--line-tight)' }],
        'sm': ['var(--font-sm)', { lineHeight: 'var(--line-normal)' }],
        'base': ['var(--font-base)', { lineHeight: 'var(--line-normal)' }],
        'lg': ['var(--font-lg)', { lineHeight: 'var(--line-normal)' }],
        'xl': ['var(--font-xl)', { lineHeight: 'var(--line-tight)' }],
        '2xl': ['var(--font-2xl)', { lineHeight: 'var(--line-tight)' }],
        '3xl': ['var(--font-3xl)', { lineHeight: 'var(--line-tight)' }],
      },
      spacing: {
        // Garden UI spacing scale
        '1': 'var(--space-1)',
        '2': 'var(--space-2)',
        '3': 'var(--space-3)',
        '4': 'var(--space-4)',
        '5': 'var(--space-5)',
        '6': 'var(--space-6)',
        '8': 'var(--space-8)',
        '10': 'var(--space-10)',
        '12': 'var(--space-12)',
        '16': 'var(--space-16)',
        '20': 'var(--space-20)',
        '24': 'var(--space-24)',
        '32': 'var(--space-32)',
      },
      maxWidth: {
        // Content widths from Garden UI
        'content': 'var(--content-width-normal)',  // 1200px
        'content-wide': 'var(--content-width-wide)', // 1600px
        'text': 'var(--width-text-optimal)',      // 65ch
      },
      borderRadius: {
        'DEFAULT': '4px',  // Garden UI default
        'sm': '2px',
        'md': '6px',
        'lg': '8px',
      },
      transitionDuration: {
        'fast': 'var(--duration-fast)',     // 150ms
        'normal': 'var(--duration-normal)', // 250ms
        'slow': 'var(--duration-slow)',     // 350ms
      },
      boxShadow: {
        'garden': '0 1px 3px var(--color-shadow)',
        'garden-lg': '0 4px 12px var(--color-shadow)',
      },
    },
  },
  plugins: [],
};
