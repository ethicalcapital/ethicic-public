// Fix for strategy card text colors in dark mode
document.addEventListener('DOMContentLoaded', function() {
  function fixStrategyCardColors() {

    // Select all strategy card headers and subtitles
    const elements = document.querySelectorAll(
      '.strategy-card .strategy-table th, ' +
            '.strategy-table .subtitle'
    );

    elements.forEach(el => {
      // Ensure both color and webkit-text-fill-color match
      el.style.setProperty('color', '#ffffff', 'important');
      el.style.setProperty('-webkit-text-fill-color', '#ffffff', 'important');
    });

    // Fix subtitles specifically
    const subtitles = document.querySelectorAll('.strategy-table .subtitle');
    subtitles.forEach(el => {
      el.style.setProperty('color', 'rgba(255, 255, 255, 0.9)', 'important');
      el.style.setProperty('-webkit-text-fill-color', 'rgba(255, 255, 255, 0.9)', 'important');
    });
  }

  // Run on page load
  fixStrategyCardColors();

  // Run when theme changes
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.attributeName === 'data-theme') {
        fixStrategyCardColors();
      }
    });
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
  });

  // Also listen for theme toggle clicks
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('garden-theme-toggle')) {
      setTimeout(fixStrategyCardColors, 100);
    }
  });
});
