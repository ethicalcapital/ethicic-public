/* ========================================
   WCAG AA ACCESSIBILITY ENHANCEMENTS FOR HTMX
   Provides screen reader announcements for dynamic content updates
   ======================================== */

(function () {
  'use strict';

  // Wait for HTMX to be available
  if (typeof htmx === 'undefined') {
    console.warn('HTMX not found - accessibility enhancements not loaded');
    return;
  }

  // ARIA live region management
  const LiveRegions = {
    polite: null,
    assertive: null,

    init() {
      // Get existing live regions from base template
      this.polite = document.getElementById('announcements');
      this.assertive = document.getElementById('urgent-announcements');

      // Create fallback regions if they don't exist
      if (!this.polite) {
        this.polite = this.createLiveRegion('announcements', 'polite');
      }
      if (!this.assertive) {
        this.assertive = this.createLiveRegion('urgent-announcements', 'assertive');
      }
    },

    createLiveRegion(id, politeness) {
      const region = document.createElement('div');
      region.id = id;
      region.setAttribute('aria-live', politeness);
      region.setAttribute('aria-atomic', 'true');
      region.className = 'sr-only';
      region.style.cssText =
        'position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden;';
      document.body.appendChild(region);
      return region;
    },

    announce(message, urgent = false) {
      const region = urgent ? this.assertive : this.polite;
      if (region) {
        // Clear and set new message
        region.textContent = '';
        setTimeout(() => {
          region.textContent = message;
        }, 100);
      }
    },

    clear() {
      if (this.polite) this.polite.textContent = '';
      if (this.assertive) this.assertive.textContent = '';
    },
  };

  // HTMX event handlers for accessibility
  const HTMXAccessibility = {
    init() {
      this.setupEventListeners();
      this.setupLoadingIndicators();
      this.setupFormValidation();
    },

    setupEventListeners() {
      // Before HTMX request - announce loading
      document.addEventListener('htmx:beforeRequest', (event) => {
        const element = event.target;
        const action = this.getActionDescription(element);
        LiveRegions.announce(`${action} Loading...`);

        // Add loading state for screen readers
        element.setAttribute('aria-busy', 'true');

        // Disable form elements during submission
        if (element.tagName === 'FORM') {
          this.disableFormElements(element, true);
        }
      });

      // After HTMX request - announce completion
      document.addEventListener('htmx:afterRequest', (event) => {
        const element = event.target;
        const xhr = event.detail.xhr;

        // Remove loading state
        element.removeAttribute('aria-busy');

        if (xhr.status >= 200 && xhr.status < 300) {
          const action = this.getActionDescription(element);
          LiveRegions.announce(`${action} completed successfully`);
        } else {
          LiveRegions.announce('Request failed. Please try again.', true);
        }

        // Re-enable form elements
        if (element.tagName === 'FORM') {
          this.disableFormElements(element, false);
        }
      });

      // After content swap - announce new content
      document.addEventListener('htmx:afterSwap', (event) => {
        const target = event.target;
        const newContent = this.getContentDescription(target);

        if (newContent) {
          LiveRegions.announce(`Content updated: ${newContent}`);
        }

        // Focus management for dynamic content
        this.manageFocusAfterSwap(target);

        // Re-initialize any new interactive elements
        this.reinitializeElements(target);
      });

      // Handle HTMX errors
      document.addEventListener('htmx:responseError', () => {
        LiveRegions.announce('An error occurred. Please try again or contact support.', true);
      });

      document.addEventListener('htmx:timeout', () => {
        LiveRegions.announce(
          'Request timed out. Please check your connection and try again.',
          true
        );
      });
    },

    setupLoadingIndicators() {
      // Enhance loading indicators with screen reader support
      document.addEventListener('htmx:beforeRequest', (event) => {
        const indicators = event.target.querySelectorAll('.htmx-indicator');
        indicators.forEach((indicator) => {
          indicator.setAttribute('aria-label', 'Loading');
          indicator.setAttribute('role', 'status');
        });
      });
    },

    setupFormValidation() {
      // Handle form validation responses
      document.addEventListener('htmx:afterSwap', (event) => {
        const target = event.target;

        // Check for error messages
        const errorElements = target.querySelectorAll('.error, .field-error, .invalid-feedback');
        if (errorElements.length > 0) {
          const errorMessages = Array.from(errorElements)
            .map((el) => el.textContent.trim())
            .filter((text) => text.length > 0)
            .join('. ');

          if (errorMessages) {
            LiveRegions.announce(`Validation errors: ${errorMessages}`, true);
          }
        }

        // Check for success messages
        const successElements = target.querySelectorAll(
          '.success, .field-success, .valid-feedback'
        );
        if (successElements.length > 0) {
          const successMessages = Array.from(successElements)
            .map((el) => el.textContent.trim())
            .filter((text) => text.length > 0)
            .join('. ');

          if (successMessages) {
            LiveRegions.announce(`Success: ${successMessages}`);
          }
        }
      });
    },

    getFormDescription(form) {
      // Helper to determine form type
      if (form.querySelector('input[type="email"]')) {
        return 'Newsletter signup';
      }
      if (form.querySelector('[name="subject"]')) {
        return 'Contact form';
      }
      return form.getAttribute('aria-label') || 'Form submission';
    },

    getActionDescription(element) {
      // Get user-friendly description of the action
      if (element.tagName === 'FORM') {
        return this.getFormDescription(element);
      }

      if (element.tagName === 'BUTTON') {
        return element.textContent.trim() || element.getAttribute('aria-label') || 'Button action';
      }

      return element.getAttribute('aria-label') || 'Content update';
    },

    getContentDescription(target) {
      // Get description of the updated content
      if (target.id === 'newsletter-response') {
        return 'Newsletter signup response';
      }

      if (target.id === 'form-response') {
        return 'Form submission response';
      }

      if (target.classList.contains('field-feedback')) {
        return 'Field validation result';
      }

      // Check for specific content types
      const headings = target.querySelectorAll('h1, h2, h3, h4, h5, h6');
      if (headings.length > 0) {
        return headings[0].textContent.trim();
      }

      return null;
    },

    manageFocusAfterSwap(target) {
      // Focus management for better keyboard navigation

      // If there's an error, focus the first error field
      const firstErrorField = target.querySelector('.error input, .error textarea, .error select');
      if (firstErrorField) {
        setTimeout(() => {
          firstErrorField.focus();
        }, 100);
        return;
      }

      // If it's a success message, focus the message for screen readers
      const successMessage = target.querySelector('.success, .alert-success');
      if (successMessage) {
        successMessage.setAttribute('tabindex', '-1');
        setTimeout(() => {
          successMessage.focus();
        }, 100);
        return;
      }

      // For newsletter signup success, focus the email input for potential re-use
      if (target.id === 'newsletter-response' && target.textContent.includes('success')) {
        const emailInput = document
          .querySelector('#newsletter-response')
          .closest('.newsletter-widget')
          .querySelector('input[type="email"]');
        if (emailInput) {
          setTimeout(() => {
            emailInput.focus();
          }, 100);
        }
      }
    },

    disableFormElements(form, disable) {
      const elements = form.querySelectorAll('input, textarea, select, button');
      elements.forEach((el) => {
        el.disabled = disable;
        if (disable) {
          el.setAttribute('aria-disabled', 'true');
        } else {
          el.removeAttribute('aria-disabled');
        }
      });
    },

    reinitializeElements(container) {
      // Re-initialize any Alpine.js or other interactive elements
      if (typeof Alpine !== 'undefined' && Alpine.initTree) {
        Alpine.initTree(container);
      }

      // Ensure all new buttons have proper ARIA attributes
      const buttons = container.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
      buttons.forEach((button) => {
        if (button.textContent.trim()) {
          button.setAttribute('aria-label', button.textContent.trim());
        }
      });

      // Ensure all new links have proper accessibility
      const links = container.querySelectorAll('a:not([aria-label]):not([aria-labelledby])');
      links.forEach((link) => {
        if (link.textContent.trim()) {
          link.setAttribute('aria-label', link.textContent.trim());
        }
      });
    },
  };

  // Newsletter-specific enhancements
  const NewsletterAccessibility = {
    init() {
      document.addEventListener('htmx:afterSwap', (event) => {
        if (event.target.id === 'newsletter-response') {
          this.handleNewsletterResponse(event.target);
        }
      });
    },

    handleNewsletterResponse(target) {
      const isSuccess =
        target.textContent.toLowerCase().includes('success') ||
        target.textContent.toLowerCase().includes('subscribed');

      if (isSuccess) {
        // Clear the email field on success
        const form = target.closest('.newsletter-widget, .newsletter-section');
        const emailInput = form?.querySelector('input[type="email"]');
        if (emailInput) {
          emailInput.value = '';
          // Update Alpine.js model if present
          if (emailInput.hasAttribute('x-model')) {
            emailInput.dispatchEvent(new Event('input'));
          }
        }
      }
    },
  };

  // Initialize when DOM is ready
  function initAccessibility() {
    LiveRegions.init();
    HTMXAccessibility.init();
    NewsletterAccessibility.init();

    // HTMX accessibility enhancements loaded
  }

  // Initialize immediately if DOM is ready, otherwise wait
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAccessibility);
  } else {
    initAccessibility();
  }
})();
