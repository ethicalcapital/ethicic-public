/*!
 * CTA Button Fix - Ensures proper styling for CTA buttons on colored backgrounds
 */

(function() {
  function fixCtaButtonStyling() {
    const ctaButtons = document.querySelectorAll('.cta-panel .garden-action.primary');

    ctaButtons.forEach(button => {
    // Force white background with purple text for visibility on purple background
      button.style.setProperty('background-color', '#ffffff', 'important');
      button.style.setProperty('color', '#3d2970', 'important');
      button.style.setProperty('border', '2px solid #ffffff', 'important');
      button.style.setProperty('-webkit-text-fill-color', '#3d2970', 'important');
      button.style.setProperty('opacity', '1', 'important');
      button.style.setProperty('visibility', 'visible', 'important');

      // Add hover effect listeners
      button.addEventListener('mouseenter', function() {
        this.style.setProperty('background-color', 'transparent', 'important');
        this.style.setProperty('color', '#ffffff', 'important');
        this.style.setProperty('-webkit-text-fill-color', '#ffffff', 'important');
      });

      button.addEventListener('mouseleave', function() {
        this.style.setProperty('background-color', '#ffffff', 'important');
        this.style.setProperty('color', '#3d2970', 'important');
        this.style.setProperty('-webkit-text-fill-color', '#3d2970', 'important');
      });
    });
  }

  // Apply on DOM content loaded
  document.addEventListener('DOMContentLoaded', fixCtaButtonStyling);

  // Also apply immediately if DOM is already loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixCtaButtonStyling);
  } else {
    fixCtaButtonStyling();
  }

  // Re-apply after any dynamic content changes
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList') {
      // Check if any CTA buttons were added
        const addedNodes = Array.from(mutation.addedNodes);
        addedNodes.forEach(node => {
          if (node.nodeType === 1) { // Element node
            const ctaButtons = node.querySelectorAll ? node.querySelectorAll('.cta-panel .garden-action.primary') : [];
            if (ctaButtons.length > 0) {
              fixCtaButtonStyling();
            }
          }
        });
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

})();
