/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html', './static/js/**/*.js', './public_site/**/*.py'],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Ethical Capital Brand Colors from Garden UI tokens
        'ec-purple': {
          DEFAULT: '#1f0322', // Primary dark purple
          light: '#2a0430', // Hover state
          pale: 'rgb(31 3 34 / 0.15)', // Alpha variant
        },
        'ec-teal': {
          DEFAULT: '#4fbbba', // CTA teal
          hover: '#5cc7c6', // Hover state
          active: '#3fa8a7', // Active state
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
        mono: [
          'var(--font-mono)',
          'ui-monospace',
          'SFMono-Regular',
          'Monaco',
          'Consolas',
          'Liberation Mono',
          'Courier New',
          'monospace',
        ],
        sans: [
          'var(--font-sans)',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      fontSize: {
        xs: ['var(--font-xs)', { lineHeight: 'var(--line-tight)' }],
        sm: ['var(--font-sm)', { lineHeight: 'var(--line-normal)' }],
        base: ['var(--font-base)', { lineHeight: 'var(--line-normal)' }],
        lg: ['var(--font-lg)', { lineHeight: 'var(--line-normal)' }],
        xl: ['var(--font-xl)', { lineHeight: 'var(--line-tight)' }],
        '2xl': ['var(--font-2xl)', { lineHeight: 'var(--line-tight)' }],
        '3xl': ['var(--font-3xl)', { lineHeight: 'var(--line-tight)' }],
      },
      spacing: {
        // Garden UI spacing scale
        1: 'var(--space-1)',
        2: 'var(--space-2)',
        3: 'var(--space-3)',
        4: 'var(--space-4)',
        5: 'var(--space-5)',
        6: 'var(--space-6)',
        8: 'var(--space-8)',
        10: 'var(--space-10)',
        12: 'var(--space-12)',
        16: 'var(--space-16)',
        20: 'var(--space-20)',
        24: 'var(--space-24)',
        32: 'var(--space-32)',
      },
      maxWidth: {
        // Content widths from Garden UI
        content: 'var(--content-width-normal)', // 1200px
        'content-wide': 'var(--content-width-wide)', // 1600px
        text: 'var(--width-text-optimal)', // 65ch
      },
      borderRadius: {
        DEFAULT: '4px', // Garden UI default
        sm: '2px',
        md: '6px',
        lg: '8px',
      },
      transitionDuration: {
        fast: 'var(--duration-fast)', // 150ms
        normal: 'var(--duration-normal)', // 250ms
        slow: 'var(--duration-slow)', // 350ms
      },
      boxShadow: {
        garden: '0 1px 3px var(--color-shadow)',
        'garden-lg': '0 4px 12px var(--color-shadow)',
      },
      typography: ({ theme }) => ({
        DEFAULT: {
          css: {
            '--tw-prose-body': theme('colors.gray[700]'),
            '--tw-prose-headings': theme('colors.gray[900]'),
            '--tw-prose-lead': theme('colors.gray[600]'),
            '--tw-prose-links': theme('colors.ec-purple.DEFAULT'),
            '--tw-prose-bold': theme('colors.gray[900]'),
            '--tw-prose-counters': theme('colors.gray[500]'),
            '--tw-prose-bullets': theme('colors.gray[300]'),
            '--tw-prose-hr': theme('colors.gray[200]'),
            '--tw-prose-quotes': theme('colors.gray[900]'),
            '--tw-prose-quote-borders': theme('colors.gray[200]'),
            '--tw-prose-captions': theme('colors.gray[500]'),
            '--tw-prose-code': theme('colors.gray[900]'),
            '--tw-prose-pre-code': theme('colors.gray[200]'),
            '--tw-prose-pre-bg': theme('colors.gray[800]'),
            '--tw-prose-th-borders': theme('colors.gray[300]'),
            '--tw-prose-td-borders': theme('colors.gray[200]'),
            maxWidth: '68ch', // Optimal reading width
            fontSize: theme('fontSize.base'),
            lineHeight: '1.7',
            p: {
              marginTop: theme('spacing.6'),
              marginBottom: theme('spacing.6'),
            },
            h1: {
              fontFamily: theme('fontFamily.mono').join(', '),
              fontWeight: '700',
              fontSize: theme('fontSize.3xl'),
              marginTop: theme('spacing.0'),
              marginBottom: theme('spacing.8'),
            },
            h2: {
              fontFamily: theme('fontFamily.mono').join(', '),
              fontWeight: '600',
              fontSize: theme('fontSize.2xl'),
              marginTop: theme('spacing.8'),
              marginBottom: theme('spacing.6'),
            },
            h3: {
              fontFamily: theme('fontFamily.mono').join(', '),
              fontWeight: '600',
              fontSize: theme('fontSize.xl'),
              marginTop: theme('spacing.6'),
              marginBottom: theme('spacing.4'),
            },
            a: {
              color: 'var(--tw-prose-links)',
              textDecoration: 'underline',
              textUnderlineOffset: '2px',
              '&:hover': {
                color: theme('colors.ec-purple.light'),
              },
            },
            blockquote: {
              borderLeftColor: theme('colors.ec-teal.DEFAULT'),
              borderLeftWidth: '4px',
              paddingLeft: theme('spacing.6'),
              fontStyle: 'italic',
              color: 'var(--tw-prose-quotes)',
            },
            code: {
              backgroundColor: theme('colors.gray[100]'),
              padding: `${theme('spacing.1')} ${theme('spacing.2')}`,
              borderRadius: theme('borderRadius.sm'),
              fontSize: theme('fontSize.sm'),
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            pre: {
              backgroundColor: 'var(--tw-prose-pre-bg)',
              color: 'var(--tw-prose-pre-code)',
              borderRadius: theme('borderRadius.lg'),
              padding: theme('spacing.6'),
              overflow: 'auto',
              fontSize: theme('fontSize.sm'),
            },
            'pre code': {
              backgroundColor: 'transparent',
              padding: '0',
            },
            ul: {
              listStyleType: 'disc',
              paddingLeft: theme('spacing.6'),
            },
            ol: {
              listStyleType: 'decimal',
              paddingLeft: theme('spacing.6'),
            },
            li: {
              marginTop: theme('spacing.2'),
              marginBottom: theme('spacing.2'),
            },
            table: {
              width: '100%',
              tableLayout: 'auto',
              marginTop: theme('spacing.8'),
              marginBottom: theme('spacing.8'),
            },
            th: {
              backgroundColor: theme('colors.gray[50]'),
              fontWeight: '600',
              padding: theme('spacing.3'),
              textAlign: 'left',
            },
            td: {
              padding: theme('spacing.3'),
            },
          },
        },
        // Dark mode variant
        invert: {
          css: {
            '--tw-prose-body': theme('colors.gray[300]'),
            '--tw-prose-headings': theme('colors.gray[100]'),
            '--tw-prose-lead': theme('colors.gray[400]'),
            '--tw-prose-links': theme('colors.ec-teal.DEFAULT'),
            '--tw-prose-bold': theme('colors.gray[100]'),
            '--tw-prose-counters': theme('colors.gray[400]'),
            '--tw-prose-bullets': theme('colors.gray[600]'),
            '--tw-prose-hr': theme('colors.gray[700]'),
            '--tw-prose-quotes': theme('colors.gray[100]'),
            '--tw-prose-quote-borders': theme('colors.gray[700]'),
            '--tw-prose-captions': theme('colors.gray[400]'),
            '--tw-prose-code': theme('colors.gray[100]'),
            '--tw-prose-pre-code': theme('colors.gray[200]'),
            '--tw-prose-pre-bg': theme('colors.gray[900]'),
            '--tw-prose-th-borders': theme('colors.gray[600]'),
            '--tw-prose-td-borders': theme('colors.gray[700]'),
            code: {
              backgroundColor: theme('colors.gray[800]'),
            },
            th: {
              backgroundColor: theme('colors.gray[800]'),
            },
          },
        },
        // Purple variant for brand alignment
        purple: {
          css: {
            '--tw-prose-links': theme('colors.ec-purple.DEFAULT'),
            '--tw-prose-quote-borders': theme('colors.ec-purple.DEFAULT'),
            blockquote: {
              borderLeftColor: theme('colors.ec-purple.DEFAULT'),
            },
          },
        },
        // Teal variant for accent content
        teal: {
          css: {
            '--tw-prose-links': theme('colors.ec-teal.DEFAULT'),
            '--tw-prose-quote-borders': theme('colors.ec-teal.DEFAULT'),
            blockquote: {
              borderLeftColor: theme('colors.ec-teal.DEFAULT'),
            },
          },
        },
      }),
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
