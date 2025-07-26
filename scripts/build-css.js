#!/usr/bin/env node

/**
 * CSS Build Process for Garden UI
 * Combines CSS files in the correct order and creates optimized builds
 */

const fs = require('fs');
const path = require('path');
const { glob } = require('glob');

// Configuration
const CONFIG = {
  inputDir: 'static/css',
  outputDir: 'static/css/dist',

  // CSS files in load order (respecting @layer cascade)
  orderedFiles: [
    // Core Garden UI files (highest priority)
    'garden-ui-theme.css',
    'garden-ui-utilities.css',
    'garden-forms.css',
    'garden-buttons-clean.css',
    'core-styles.css',

    // Component-specific files
    'garden-blog.css',
    'garden-widgets.css',
    'garden-data-table.css',

    // Page-specific files (lower priority)
    'onboarding-forms-clean.css',
    'process-page.css',

    // Layer-specific files (clean versions only)
    'layers/*-clean.css',

    // Clean homepage implementation
    '16-homepage-clean.css',

    // Utility and layout files
    'utility-layout.css',
    'public-site-layout-fixes.css',
    'public-site-modular.css',

    // Keep only essential fixes during migration
    'footer-clean.css',
    'wcag-contrast-clean.css',
    'accessibility-contrast-fixes-clean.css',
    'container-structure-enhancements.css',
    'search-clean.css',
    'mobile-responsive-clean.css',
    'fix-white-line.css',
    'login-dropdown-clean.css',
    'cta-tiffany-blue.css'
  ],

  // Files to exclude from build
  excludePatterns: [
    'dist/**',
    'backup-*/**',
    'archived/**',
    // Legacy override files
    'z-*.css',
    '*-nuclear-*.css',
    '*-emergency-*.css',
    'button-contrast-fixes.css',
    'critical-fouc-prevention.css',
    'mobile-menu-clean.css',
    'header-height-fix.css',
    'page-width-fix.css',
    'mobile-nav-fix.css',
    'header-text-fix.css',
    'strategy-nuclear-fix.css',
    'strategy-table-contrast-fix.css',
    'button-alignment-fix.css',
    // Exclude problematic layer files with html body selectors
    'layers/40-adviser-page.css',
    'layers/*-nuclear-*.css',
    'layers/*-fix.css',
    // Exclude original files replaced by clean versions
    '16-homepage.css',
    'accessibility-contrast-fixes.css',
    'login-dropdown-fix.css',
    'process-dark-mode-fix.css',
    'footer-fix.css',
    'search-fixes.css',
    'search-visibility-ultimate-fix.css',
    'mobile-full-width.css',
    'onboarding-comprehensive.css',
    'wcag-contrast-fixes.css'
  ]
};

/**
 * Ensure output directory exists
 */
function ensureOutputDir() {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    console.log(`✅ Created output directory: ${CONFIG.outputDir}`);
  }
}

/**
 * Get all CSS files in the input directory
 */
async function getAllCSSFiles() {
  const pattern = path.join(CONFIG.inputDir, '**/*.css');
  const files = await glob(pattern);

  // Filter out excluded files
  const excludeRegexes = CONFIG.excludePatterns.map(pattern =>
    new RegExp(pattern.replace(/\*/g, '.*'))
  );

  return files.filter(file => {
    const relativePath = path.relative(CONFIG.inputDir, file);
    return !excludeRegexes.some(regex => regex.test(relativePath));
  });
}

/**
 * Order files according to configuration
 */
function orderFiles(files) {
  const orderedFiles = [];
  const remainingFiles = [...files];

  // Add files in specified order
  for (const pattern of CONFIG.orderedFiles) {
    const fullPattern = path.join(CONFIG.inputDir, pattern);
    const matchingFiles = files.filter(file => {
      if (pattern.includes('*')) {
        const regex = new RegExp(fullPattern.replace(/\*/g, '.*'));
        return regex.test(file);
      } else {
        return file === fullPattern;
      }
    });

    for (const file of matchingFiles) {
      if (remainingFiles.includes(file)) {
        orderedFiles.push(file);
        remainingFiles.splice(remainingFiles.indexOf(file), 1);
      }
    }
  }

  // Add any remaining files
  orderedFiles.push(...remainingFiles);

  return orderedFiles;
}

/**
 * Read and combine CSS files
 */
function combineCSS(files) {
  let combinedCSS = '';

  console.log('📦 Combining CSS files:');

  for (const file of files) {
    if (fs.existsSync(file)) {
      const content = fs.readFileSync(file, 'utf8');
      const relativePath = path.relative(CONFIG.inputDir, file);

      // Add file header comment
      combinedCSS += `/* ===== ${relativePath} ===== */\n`;
      combinedCSS += content;
      combinedCSS += '\n\n';

      console.log(`  ✅ ${relativePath}`);
    } else {
      console.log(`  ⚠️  File not found: ${file}`);
    }
  }

  return combinedCSS;
}

/**
 * Add CSS layers to combined output - fixed to avoid nesting
 */
function addCSSLayers(css) {
  const layeredCSS = `/* CSS Layers for proper cascade control */
@layer reset, tokens, themes, base, components, utilities, overrides;

/* Combined Garden UI CSS - no wrapping layer to avoid nesting */
${css}
`;

  return layeredCSS;
}

/**
 * Main build function
 */
async function build() {
  console.log('🚀 Starting CSS build process...');
  console.log('================================');

  try {
    // Ensure output directory exists
    ensureOutputDir();

    // Get all CSS files
    const allFiles = await getAllCSSFiles();
    console.log(`📁 Found ${allFiles.length} CSS files`);

    // Order files according to configuration
    const orderedFiles = orderFiles(allFiles);

    // Combine CSS files
    const combinedCSS = combineCSS(orderedFiles);

    // Add CSS layers
    const layeredCSS = addCSSLayers(combinedCSS);

    // Write combined CSS
    const outputPath = path.join(CONFIG.outputDir, 'combined.css');
    fs.writeFileSync(outputPath, layeredCSS);

    console.log('');
    console.log('✅ Build completed successfully!');
    console.log(`📄 Combined CSS: ${outputPath}`);
    console.log(`📊 Total size: ${(layeredCSS.length / 1024).toFixed(2)} KB`);

    // Create development version (unminified)
    const devPath = path.join(CONFIG.outputDir, 'development.css');
    fs.writeFileSync(devPath, layeredCSS);
    console.log(`📄 Development CSS: ${devPath}`);

    return outputPath;

  } catch (error) {
    console.error('❌ Build failed:', error);
    process.exit(1);
  }
}

// Run build if called directly
if (require.main === module) {
  build();
}

module.exports = { build };
