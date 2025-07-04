module.exports = [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: "script",
      globals: {
        // Browser globals
        window: "readonly",
        document: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        setInterval: "readonly",
        clearTimeout: "readonly",
        clearInterval: "readonly",
        localStorage: "readonly",
        sessionStorage: "readonly",
        location: "readonly",
        navigator: "readonly",
        history: "readonly",
        alert: "readonly",
        confirm: "readonly",
        prompt: "readonly",
        fetch: "readonly",
        XMLHttpRequest: "readonly",
        FormData: "readonly",
        URL: "readonly",
        URLSearchParams: "readonly",
        // Common libraries
        Alpine: "readonly",
        htmx: "readonly",
        // Custom globals
        MutationObserver: "readonly",
        IntersectionObserver: "readonly",
        ResizeObserver: "readonly"
      }
    },
    rules: {
      // Error prevention
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
      "no-console": "off", // Allow console for debugging
      "no-debugger": "error",
      "no-dupe-args": "error",
      "no-dupe-keys": "error",
      "no-duplicate-case": "error",
      "no-empty": "error",
      "no-extra-semi": "error",
      "no-func-assign": "error",
      "no-irregular-whitespace": "error",
      "no-unreachable": "error",
      "use-isnan": "error",
      "valid-typeof": "error",
      
      // Best practices
      "eqeqeq": ["error", "always", {"null": "ignore"}],
      "no-alert": "warn",
      "no-eval": "error",
      "no-implied-eval": "error",
      "no-return-assign": "error",
      "no-self-assign": "error",
      "no-self-compare": "error",
      "no-unused-expressions": "error",
      
      // Stylistic
      "indent": ["error", 2],
      "quotes": ["error", "single", { "avoidEscape": true }],
      "semi": ["error", "always"],
      "comma-dangle": ["error", "only-multiline"],
      "no-trailing-spaces": "error",
      "no-multiple-empty-lines": ["error", { "max": 2 }]
    }
  }
];