/*!
 * Garden Core JavaScript Framework
 * High-performance keyboard-centric interactions
 * Optimized for terminal aesthetic and speed
 */

/* global MutationObserver */

(function (window, document) {
  'use strict';

  // Global Garden namespace with backward compatibility
  window.Garden = window.Garden || {};
  window.DEWEY = window.DEWEY || {}; // Backward compatibility

  // Configuration
  const CONFIG = {
    debug: window.Garden.debug || window.DEWEY.debug || false,
    hotkeys: {
      search: '/',
      help: '?',
      escape: 'Escape',
      up: 'j',
      down: 'k',
      left: 'h',
      right: 'l',
      enter: 'Enter',
      plus: '=',
      minus: '-'
    },
    selectors: {
      sidebar: '#sidebar',
      searchInput: '#search-input',
      navigableItems: '.nav-item, .data-table tr, .list-item',
      focusable: 'input, button, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
    }
  };

  // Utility functions
  const Utils = {
    log: function (_message, _data) {
      if (CONFIG.debug) {
        // Debug: [Garden] message
      }
    },

    debounce: function (func, wait) {
      let timeout;
      return function executedFunction (...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },

    throttle: function (func, limit) {
      let inThrottle;
      return function () {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
          func.apply(context, args);
          inThrottle = true;
          setTimeout(() => {
            inThrottle = false;
          }, limit);
        }
      };
    },

    addClass: function (element, className) {
      if (element && element.classList) {
        element.classList.add(className);
      }
    },

    removeClass: function (element, className) {
      if (element && element.classList) {
        element.classList.remove(className);
      }
    },

    hasClass: function (element, className) {
      return element && element.classList && element.classList.contains(className);
    },

    toggleClass: function (element, className) {
      if (element && element.classList) {
        element.classList.toggle(className);
      }
    },

    getParent: function (element, selector) {
      while (element && element !== document) {
        if (element.matches && element.matches(selector)) {
          return element;
        }
        element = element.parentNode;
      }
      return null;
    },

    preventDefault: function (event) {
      if (event.preventDefault) {
        event.preventDefault();
      }
      event.returnValue = false;
    }
  };

  // Keyboard Navigation Manager
  const KeyboardNav = {
    currentIndex: 0,
    items: [],
    active: false,

    init: function () {
      this.bindEvents();
      this.updateItems();
      Utils.log('Keyboard navigation initialized');
    },

    bindEvents: function () {
      document.addEventListener('keydown', this.handleKeyDown.bind(this));
      document.addEventListener('click', this.handleClick.bind(this));

      // Update items when DOM changes
      if (typeof MutationObserver !== 'undefined') {
        const observer = new MutationObserver(Utils.debounce(() => {
          this.updateItems();
        }, 100));

        observer.observe(document.body, {
          childList: true,
          subtree: true
        });
      }
    },

    updateItems: function () {
      this.items = Array.from(document.querySelectorAll(CONFIG.selectors.navigableItems));
      this.items = this.items.filter(item => {
        return item.offsetParent !== null; // Visible items only
      });
      Utils.log('Navigation items updated', this.items.length);
    },

    getKeyAction: function(key) {
      const actions = {
        [CONFIG.hotkeys.up]: () => this.navigate(-1),
        [CONFIG.hotkeys.down]: () => this.navigate(1),
        [CONFIG.hotkeys.enter]: () => this.activate(),
        [CONFIG.hotkeys.search]: () => this.focusSearch(),
        [CONFIG.hotkeys.help]: () => this.showHelp(),
        [CONFIG.hotkeys.escape]: () => this.escape(),
        [CONFIG.hotkeys.plus]: () => this.adjustValue(1),
        [CONFIG.hotkeys.minus]: () => this.adjustValue(-1)
      };
      return actions[key];
    },

    handleKeyDown: function (event) {
      // Don't interfere when user is typing
      if (this.isTyping(event.target)) {
        return;
      }

      const key = event.key.toLowerCase();
      const action = this.getKeyAction(key);

      if (action) {
        action();
        Utils.preventDefault(event);
      }
    },

    handleClick: function (event) {
      const item = Utils.getParent(event.target, CONFIG.selectors.navigableItems);
      if (item) {
        const index = this.items.indexOf(item);
        if (index !== -1) {
          this.setActive(index);
        }
      }
    },

    handleKeyboard: function (event) {
      this.handleKeyDown(event);
    },

    getActive: function () {
      return this.currentIndex;
    },

    next: function () {
      this.navigate(1);
    },

    prev: function () {
      this.navigate(-1);
    },

    isTyping: function (element) {
      if (!element || !element.tagName) {
        return false;
      }

      const tagName = element.tagName.toLowerCase();
      const type = element.type ? element.type.toLowerCase() : '';

      // Comprehensive list of input types where users can type
      const typingInputTypes = [
        'text', 'email', 'password', 'search', 'url', 'number', 
        'tel', 'date', 'datetime-local', 'month', 'time', 'week',
        'color' // color picker can have manual input in some browsers
      ];

      return (
        tagName === 'input' && typingInputTypes.includes(type)
      ) ||
            tagName === 'textarea' ||
            tagName === 'select' || // Select elements should also disable keyboard nav
            element.contentEditable === 'true' ||
            element.isContentEditable === true ||
            // Check for ARIA role that indicates editable content
            element.getAttribute('role') === 'textbox' ||
            element.getAttribute('role') === 'searchbox';
    },

    navigate: function (direction) {
      if (this.items.length === 0) {
        this.updateItems();
        return;
      }

      const newIndex = this.currentIndex + direction;

      if (newIndex >= 0 && newIndex < this.items.length) {
        this.setActive(newIndex);
      } else if (direction > 0) {
        this.setActive(0); // Wrap to beginning
      } else {
        this.setActive(this.items.length - 1); // Wrap to end
      }
    },

    setActive: function (index) {
      // Remove previous active state
      this.items.forEach(item => {
        Utils.removeClass(item, 'keyboard-active');
        item.setAttribute('tabindex', '-1');
      });

      this.currentIndex = Math.max(0, Math.min(index, this.items.length - 1));
      const activeItem = this.items[this.currentIndex];

      if (activeItem) {
        Utils.addClass(activeItem, 'keyboard-active');
        activeItem.setAttribute('tabindex', '0');
        activeItem.focus();
        this.scrollIntoView(activeItem);
        this.active = true;
      }

      Utils.log('Active item set', this.currentIndex);
    },

    activate: function () {
      const activeItem = this.items[this.currentIndex];
      if (activeItem) {
        const link = activeItem.querySelector('a');
        const button = activeItem.querySelector('button');

        if (link) {
          link.click();
        } else if (button) {
          button.click();
        } else if (activeItem.click) {
          activeItem.click();
        }
      }
    },

    scrollIntoView: function (element) {
      if (element && element.scrollIntoView) {
        element.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        });
      }
    },

    focusSearch: function () {
      const searchInput = document.querySelector(CONFIG.selectors.searchInput) ||
                              document.querySelector('input[type="search"]') ||
                              document.querySelector('input[placeholder*="search"]');

      if (searchInput) {
        searchInput.focus();
        Utils.log('Search focused');
      } else {
        // Create temporary search overlay
        this.createSearchOverlay();
      }
    },

    createSearchOverlay: function () {
      const overlay = document.createElement('div');
      overlay.id = 'search-overlay';
      overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: var(--color-shadow);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;

      const searchBox = document.createElement('div');
      searchBox.style.cssText = `
                background: var(--color-surface);
                padding: var(--space-6);
                border-radius: var(--radius);
                border: 2px solid var(--color-primary);
                min-width: 400px;
            `;

      const input = document.createElement('input');
      input.type = 'search';
      input.placeholder = 'Search...';
      input.style.cssText = `
                width: 100%;
                font-size: var(--font-lg);
                padding: var(--space-3);
                border: 2px solid var(--color-border);
                border-radius: var(--radius);
                font-family: var(--font-mono);
            `;

      searchBox.appendChild(input);
      overlay.appendChild(searchBox);
      document.body.appendChild(overlay);

      input.focus();

      const closeOverlay = () => {
        document.body.removeChild(overlay);
      };

      overlay.addEventListener('click', function (e) {
        if (e.target === overlay) {
          closeOverlay();
        }
      });

      input.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
          closeOverlay();
        }
      });

      Utils.log('Search overlay created');
    },

    showHelp: function () {
      const helpOverlay = document.createElement('div');
      helpOverlay.id = 'help-overlay';
      helpOverlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: var(--color-shadow);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;

      const helpBox = document.createElement('div');
      helpBox.style.cssText = `
                background: var(--color-surface);
                padding: var(--space-6);
                border-radius: var(--radius);
                border: 2px solid var(--color-primary);
                max-width: 500px;
                font-family: var(--font-mono);
            `;

      helpBox.innerHTML = `
                <h3 style="color: var(--color-primary); margin-bottom: var(--space-4);">Keyboard Shortcuts</h3>
                <div style="display: grid; grid-template-columns: 1fr 2fr; gap: var(--space-2); font-size: var(--font-sm);">
                    <div><kbd style="background: var(--color-surface-variant); padding: 2px 6px; border-radius: 3px;">J/K</kbd></div>
                    <div>Navigate up/down</div>
                    <div><kbd style="background: var(--color-surface-variant); padding: 2px 6px; border-radius: 3px;">/</kbd></div>
                    <div>Search</div>
                    <div><kbd style="background: var(--color-surface-variant); padding: 2px 6px; border-radius: 3px;">Enter</kbd></div>
                    <div>Activate/Select</div>
                    <div><kbd style="background: var(--color-surface-variant); padding: 2px 6px; border-radius: 3px;">+/-</kbd></div>
                    <div>Adjust values</div>
                    <div><kbd style="background: var(--color-surface-variant); padding: 2px 6px; border-radius: 3px;">Esc</kbd></div>
                    <div>Cancel/Close</div>
                    <div><kbd style="background: var(--color-surface-variant); padding: 2px 6px; border-radius: 3px;">?</kbd></div>
                    <div>Show this help</div>
                </div>
                <div style="margin-top: var(--space-4); text-align: center;">
                    <button style="background: var(--ec-purple); color: white; padding: var(--space-2) var(--space-4); border: none; border-radius: var(--radius); cursor: pointer;">Close</button>
                </div>
            `;

      helpOverlay.appendChild(helpBox);
      document.body.appendChild(helpOverlay);

      const closeHelp = () => {
        document.body.removeChild(helpOverlay);
      };

      helpBox.querySelector('button').addEventListener('click', closeHelp);
      helpOverlay.addEventListener('click', function (e) {
        if (e.target === helpOverlay) {
          closeHelp();
        }
      });

      Utils.log('Help overlay shown');
    },

    escape: function () {
      // Close any overlays
      const overlays = document.querySelectorAll('#search-overlay, #help-overlay');
      overlays.forEach(overlay => {
        if (overlay.parentNode) {
          overlay.parentNode.removeChild(overlay);
        }
      });

      // Blur any focused input
      if (document.activeElement && this.isTyping(document.activeElement)) {
        document.activeElement.blur();
      }

      // Clear any selections
      if (window.getSelection) {
        window.getSelection().removeAllRanges();
      }

      Utils.log('Escape action performed');
    },

    adjustValue: function (direction) {
      const activeElement = document.activeElement;

      if (activeElement && activeElement.type === 'number') {
        const currentValue = parseFloat(activeElement.value) || 0;
        const step = parseFloat(activeElement.step) || 1;
        const newValue = currentValue + (direction * step);

        // Respect min/max constraints
        const min = activeElement.min ? parseFloat(activeElement.min) : -Infinity;
        const max = activeElement.max ? parseFloat(activeElement.max) : Infinity;

        activeElement.value = Math.max(min, Math.min(max, newValue));

        // Trigger change event
        const event = new Event('change', { bubbles: true });
        activeElement.dispatchEvent(event);

        Utils.log('Value adjusted', activeElement.value);
      }
    }
  };

  // Performance Monitor
  const Performance = {
    init: function () {
      this.measurePageLoad();
      this.monitorInteractions();
    },

    mark: function (name) {
      if (window.performance && window.performance.mark) {
        window.performance.mark(name);
      }
      Utils.log('Performance mark', name);
    },

    measure: function (name, startMark, endMark) {
      if (window.performance && window.performance.measure) {
        window.performance.measure(name, startMark, endMark);
      }
      Utils.log('Performance measure', name);
    },

    measurePageLoad: function () {
      window.addEventListener('load', function () {
        if (window.performance && window.performance.timing) {
          const timing = window.performance.timing;
          const loadTime = timing.loadEventEnd - timing.navigationStart;

          Utils.log('Page load time', loadTime + 'ms');

          // Update status in footer
          setTimeout(() => {
            const statusElement = document.getElementById('connection-status');
            if (statusElement) {
              statusElement.textContent = `Loaded in ${loadTime}ms`;
            }
          }, 100);
        }
      });
    },

    monitorInteractions: function () {
      // Track keyboard response times
      let keydownTime = 0;

      document.addEventListener('keydown', function () {
        keydownTime = performance.now();
      });

      document.addEventListener('keyup', function () {
        if (keydownTime) {
          const responseTime = performance.now() - keydownTime;
          if (responseTime > 100) { // Log slow responses
            Utils.log('Slow keyboard response', responseTime + 'ms');
          }
        }
      });
    }
  };

  // Form Enhancements
  const Forms = {
    init: function () {
      this.enhanceNumberInputs();
      this.enhanceFormValidation();
    },

    enhance: function (form) {
      if (!form) return;

      // Enhance number inputs in this form
      const numberInputs = form.querySelectorAll('input[type="number"]');
      numberInputs.forEach(input => {
        this.enhanceNumberInput(input);
      });

      Utils.log('Form enhanced', form);
    },

    validate: function (form) {
      if (!form) return true;

      const isValid = form.checkValidity ? form.checkValidity() : true;

      if (!isValid) {
        // Focus first invalid field
        const firstInvalid = form.querySelector(':invalid');
        if (firstInvalid && firstInvalid.focus) {
          firstInvalid.focus();
        }
      }

      Utils.log('Form validation', { form, isValid });
      return isValid;
    },

    enhanceNumberInput: function (input) {
      if (!input || input.getAttribute('data-enhanced')) return;

      input.setAttribute('data-enhanced', 'true');

      // Add visual indicator for keyboard shortcuts
      const wrapper = document.createElement('div');
      wrapper.style.position = 'relative';
      wrapper.style.display = 'inline-block';

      if (input.parentNode) {
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const hint = document.createElement('span');
        hint.textContent = '+/-';
        hint.style.cssText = `
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 10px;
          color: var(--ec-text-muted);
          pointer-events: none;
        `;

        wrapper.appendChild(hint);
      }
    },

    enhanceNumberInputs: function () {
      const numberInputs = document.querySelectorAll('input[type="number"]');
      numberInputs.forEach(input => {
        this.enhanceNumberInput(input);
      });
    },

    enhanceFormValidation: function () {
      const forms = document.querySelectorAll('form');

      forms.forEach(form => {
        form.addEventListener('submit', function (e) {
          const isValid = form.checkValidity();

          if (!isValid) {
            e.preventDefault();

            // Focus first invalid field
            const firstInvalid = form.querySelector(':invalid');
            if (firstInvalid) {
              firstInvalid.focus();
            }
          }
        });
      });
    }
  };

  // Initialize everything when DOM is ready
  function init () {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
      return;
    }

    Utils.log('Garden Core initializing...');

    KeyboardNav.init();
    Performance.init();
    Forms.init();

    // Set initial focus
    setTimeout(() => {
      const firstNavigable = document.querySelector(CONFIG.selectors.navigableItems);
      if (firstNavigable) {
        KeyboardNav.setActive(0);
      }
    }, 100);

    Utils.log('Garden Core initialized');

    // Expose public API - both Garden and DEWEY namespaces
    window.Garden.keyboard = KeyboardNav;
    window.Garden.utils = Utils;
    window.Garden.performance = Performance;
    window.Garden.forms = Forms;

    // Backward compatibility
    window.DEWEY.keyboard = KeyboardNav;
    window.DEWEY.utils = Utils;
    window.DEWEY.performance = Performance;
    window.DEWEY.forms = Forms;
  }

  // Auto-initialize
  init();

  // Export for CommonJS (testing)
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      Garden: window.Garden,
      DEWEY: window.DEWEY,
      init,
      CONFIG
    };
  }
})(window, document);
