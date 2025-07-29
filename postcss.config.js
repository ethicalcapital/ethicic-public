module.exports = {
  plugins: [
    // Tailwind CSS processing
    require("@tailwindcss/postcss"),

    // Support for CSS nesting
    require("postcss-nested"),

    // Support for CSS custom properties
    require("postcss-custom-properties")({
      preserve: true, // Keep custom properties for runtime theming
    }),

    // Autoprefixer for vendor prefixes
    require("autoprefixer"),

    // CSS optimization (only in production)
    ...(process.env.NODE_ENV === "production"
      ? [
          require("cssnano")({
            preset: [
              "default",
              {
                discardComments: {
                  removeAll: true,
                },
                normalizeWhitespace: false,
                colormin: false,
                minifyFontValues: false,
                // Preserve CSS layers
                discardDuplicates: false,
                mergeRules: false,
                // Don't break CSS custom properties
                reduceIdents: false,
                zindex: false,
              },
            ],
          }),
        ]
      : []),
  ],
};
