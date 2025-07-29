/* ========================================
   WCAG AA FOCUS TRAPPING FOR MODALS AND OVERLAYS
   Provides proper focus management for modal dialogs and dropdowns
   ======================================== */

(function () {
  'use strict';

  // Focus Trap Manager
  const FocusTrap = {
    activeTraps: [],

    // Create a focus trap for an element
    create(element, options = {}) {
      const trap = new FocusTrapInstance(element, options);
      this.activeTraps.push(trap);
      return trap;
    },

    // Remove a specific focus trap
    remove(trap) {
      const index = this.activeTraps.indexOf(trap);
      if (index > -1) {
        this.activeTraps.splice(index, 1);
        trap.destroy();
      }
    },

    // Remove all focus traps
    removeAll() {
      this.activeTraps.forEach((trap) => trap.destroy());
      this.activeTraps = [];
    },

    // Get the currently active focus trap
    getActive() {
      return this.activeTraps[this.activeTraps.length - 1] || null;
    },
  };

  // Individual Focus Trap Instance
  class FocusTrapInstance {
    constructor(element, options = {}) {
      this.element = element;
      this.options = {
        initialFocus: options.initialFocus || null,
        returnFocus: options.returnFocus !== false,
        allowOutsideClick: options.allowOutsideClick || false,
        escapeKey: options.escapeKey !== false,
        ...options,
      };

      this.previouslyFocusedElement = document.activeElement;
      this.isActive = false;

      this.boundHandleKeydown = this.handleKeydown.bind(this);
      this.boundHandleClick = this.handleClick.bind(this);

      this.activate();
    }

    activate() {
      if (this.isActive) return;

      this.isActive = true;
      this.updateFocusableElements();

      // Add event listeners
      document.addEventListener('keydown', this.boundHandleKeydown, true);
      if (!this.options.allowOutsideClick) {
        document.addEventListener('click', this.boundHandleClick, true);
      }

      // Set initial focus
      this.setInitialFocus();

      // Add role and aria attributes if not present
      if (!this.element.getAttribute('role')) {
        this.element.setAttribute('role', 'dialog');
      }
      if (!this.element.getAttribute('aria-modal')) {
        this.element.setAttribute('aria-modal', 'true');
      }

      // Hide other content from screen readers
      this.hideOtherContent();
    }

    deactivate() {
      if (!this.isActive) return;

      this.isActive = false;

      // Remove event listeners
      document.removeEventListener('keydown', this.boundHandleKeydown, true);
      document.removeEventListener('click', this.boundHandleClick, true);

      // Restore focus
      if (this.options.returnFocus && this.previouslyFocusedElement) {
        this.previouslyFocusedElement.focus();
      }

      // Restore other content visibility
      this.restoreOtherContent();
    }

    destroy() {
      this.deactivate();
    }

    updateFocusableElements() {
      const focusableSelectors = [
        'button:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        'a[href]',
        '[tabindex]:not([tabindex="-1"])',
        '[contenteditable="true"]',
      ];

      this.focusableElements = Array.from(
        this.element.querySelectorAll(focusableSelectors.join(','))
      ).filter((el) => {
        return this.isVisible(el) && !el.hasAttribute('aria-hidden');
      });

      this.firstFocusableElement = this.focusableElements[0];
      this.lastFocusableElement = this.focusableElements[this.focusableElements.length - 1];
    }

    isVisible(element) {
      const style = window.getComputedStyle(element);
      return (
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        style.opacity !== '0' &&
        element.offsetParent !== null
      );
    }

    setInitialFocus() {
      let targetElement = null;

      // Use specified initial focus element
      if (this.options.initialFocus) {
        if (typeof this.options.initialFocus === 'string') {
          targetElement = this.element.querySelector(this.options.initialFocus);
        } else if (this.options.initialFocus.nodeType) {
          targetElement = this.options.initialFocus;
        }
      }

      // Fallback to first focusable element
      if (!targetElement) {
        targetElement = this.firstFocusableElement;
      }

      // Fallback to the container itself
      if (!targetElement) {
        targetElement = this.element;
        this.element.setAttribute('tabindex', '-1');
      }

      if (targetElement) {
        // Use a small delay to ensure the element is ready
        setTimeout(() => {
          targetElement.focus();
        }, 10);
      }
    }

    handleKeydown(event) {
      if (!this.isActive) return;

      // Handle Escape key
      if (event.key === 'Escape' && this.options.escapeKey) {
        event.preventDefault();
        this.deactivate();
        return;
      }

      // Handle Tab key for focus trapping
      if (event.key === 'Tab') {
        this.handleTabKey(event);
      }
    }

    handleTabKey(event) {
      this.updateFocusableElements();

      if (this.focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      if (this.focusableElements.length === 1) {
        event.preventDefault();
        this.focusableElements[0].focus();
        return;
      }

      const currentIndex = this.focusableElements.indexOf(document.activeElement);

      if (event.shiftKey) {
        // Shift + Tab (backward)
        if (currentIndex <= 0) {
          event.preventDefault();
          this.lastFocusableElement.focus();
        }
      } else {
        // Tab (forward)
        if (currentIndex >= this.focusableElements.length - 1) {
          event.preventDefault();
          this.firstFocusableElement.focus();
        }
      }
    }

    handleClick(event) {
      if (!this.element.contains(event.target)) {
        event.preventDefault();
        event.stopPropagation();
      }
    }

    hideOtherContent() {
      this.hiddenElements = [];
      const siblings = Array.from(document.body.children).filter(
        (child) =>
          child !== this.element && !this.element.contains(child) && !child.contains(this.element)
      );

      siblings.forEach((sibling) => {
        if (!sibling.hasAttribute('aria-hidden')) {
          sibling.setAttribute('aria-hidden', 'true');
          this.hiddenElements.push(sibling);
        }
      });
    }

    restoreOtherContent() {
      if (this.hiddenElements) {
        this.hiddenElements.forEach((element) => {
          element.removeAttribute('aria-hidden');
        });
        this.hiddenElements = [];
      }
    }
  }

  // Auto-initialize for common modal patterns
  const AutoInitializer = {
    init() {
      this.initializeDialogs();
      this.initializeDropdowns();
      this.initializeModals();
    },

    initializeDialogs() {
      // Auto-trap focus for elements with dialog role
      document.addEventListener('DOMContentLoaded', () => {
        const dialogs = document.querySelectorAll('[role="dialog"]');
        dialogs.forEach((dialog) => {
          if (this.isVisible(dialog) && !dialog.hasAttribute('data-focus-trap-initialized')) {
            FocusTrap.create(dialog);
            dialog.setAttribute('data-focus-trap-initialized', 'true');
          }
        });
      });
    },

    initializeDropdowns() {
      // Handle Alpine.js dropdowns
      document.addEventListener('alpine:init', () => {
        // This will be enhanced when Alpine.js is available
        if (typeof Alpine !== 'undefined') {
          Alpine.directive('focus-trap', (el, _directive, { cleanup }) => {
            let trap = null;

            const createTrap = () => {
              if (!trap && this.isVisible(el)) {
                trap = FocusTrap.create(el, {
                  initialFocus: el.querySelector('[x-ref="firstFocusable"]'),
                  returnFocus: true,
                });
              }
            };

            const removeTrap = () => {
              if (trap) {
                FocusTrap.remove(trap);
                trap = null;
              }
            };

            // Watch for visibility changes
            const observer = new MutationObserver(() => {
              if (this.isVisible(el)) {
                createTrap();
              } else {
                removeTrap();
              }
            });

            observer.observe(el, {
              attributes: true,
              attributeFilter: ['style', 'class'],
            });

            cleanup(() => {
              removeTrap();
              observer.disconnect();
            });
          });
        }
      });
    },

    initializeModals() {
      // Handle HTMX modal responses
      document.addEventListener('htmx:afterSwap', (event) => {
        const modals = event.target.querySelectorAll('.modal, [role="dialog"], [data-focus-trap]');
        modals.forEach((modal) => {
          if (this.isVisible(modal)) {
            FocusTrap.create(modal);
          }
        });
      });
    },

    isVisible(element) {
      const style = window.getComputedStyle(element);
      return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    },
  };

  // Notification dropdown specific enhancement
  const NotificationDropdownEnhancer = {
    init() {
      document.addEventListener('alpine:init', () => {
        // Enhance notification bell dropdowns
        const bells = document.querySelectorAll('.notification-bell');
        bells.forEach((bell) => {
          this.enhanceNotificationBell(bell);
        });
      });
    },

    enhanceNotificationBell(bell) {
      const dropdown = bell.querySelector('.notification-dropdown');
      if (!dropdown) return;

      let trap = null;

      // Create observer for dropdown visibility
      const observer = new MutationObserver(() => {
        const isVisible = dropdown.style.display !== 'none' && dropdown.offsetParent !== null;

        if (isVisible && !trap) {
          trap = FocusTrap.create(dropdown, {
            initialFocus: dropdown.querySelector('[x-ref="firstFocusable"]'),
            returnFocus: true,
            escapeKey: true,
          });
        } else if (!isVisible && trap) {
          FocusTrap.remove(trap);
          trap = null;
        }
      });

      observer.observe(dropdown, {
        attributes: true,
        attributeFilter: ['style', 'class'],
        childList: true,
      });
    },
  };

  // Public API
  window.FocusTrap = FocusTrap;
  window.FocusTrapInstance = FocusTrapInstance;

  // Initialize when DOM is ready
  function initFocusTrapping() {
    AutoInitializer.init();
    NotificationDropdownEnhancer.init();

    // Focus trapping accessibility enhancements loaded
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFocusTrapping);
  } else {
    initFocusTrapping();
  }
})();
