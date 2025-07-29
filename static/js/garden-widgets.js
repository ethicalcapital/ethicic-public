/**
 * Garden UI Widgets JavaScript Library
 * Provides interactive functionality for Garden UI components
 */

// Theme Management
window.GardenUI = {
  // Initialize Garden UI components
  init: function () {
    this.initThemeToggle();
    this.initModals();
    this.initTabs();
    this.initTooltips();
    this.initNotifications();
  },

  // Theme toggle functionality
  initThemeToggle: function () {
    const toggles = document.querySelectorAll("[data-theme-toggle]");
    toggles.forEach((toggle) => {
      toggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("garden-theme", newTheme);
      });
    });

    // Load saved theme
    const savedTheme = localStorage.getItem("garden-theme");
    if (savedTheme) {
      document.documentElement.setAttribute("data-theme", savedTheme);
    }
  },

  // Modal functionality
  initModals: function () {
    // Modal triggers
    const modalTriggers = document.querySelectorAll("[data-modal-target]");
    modalTriggers.forEach((trigger) => {
      trigger.addEventListener("click", (e) => {
        e.preventDefault();
        const targetId = trigger.getAttribute("data-modal-target");
        this.showModal(targetId);
      });
    });

    // Modal close buttons
    const closeButtons = document.querySelectorAll("[data-modal-close]");
    closeButtons.forEach((button) => {
      button.addEventListener("click", () => {
        this.hideModal(button.closest(".terminal-modal"));
      });
    });

    // Close modal on backdrop click
    const modals = document.querySelectorAll(".terminal-modal");
    modals.forEach((modal) => {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) {
          this.hideModal(modal);
        }
      });
    });
  },

  showModal: function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("terminal-modal-hidden");
      modal.classList.add("terminal-modal-flex");
      document.body.style.overflow = "hidden";
    }
  },

  hideModal: function (modal) {
    if (typeof modal === "string") {
      modal = document.getElementById(modal);
    }
    if (modal) {
      modal.classList.remove("terminal-modal-flex");
      modal.classList.add("terminal-modal-hidden");
      document.body.style.overflow = "";
    }
  },

  // Tab functionality
  initTabs: function () {
    const tabContainers = document.querySelectorAll("[data-tabs]");
    tabContainers.forEach((container) => {
      const tabs = container.querySelectorAll("[data-tab]");
      const panels = container.querySelectorAll("[data-tab-panel]");

      tabs.forEach((tab) => {
        tab.addEventListener("click", (e) => {
          e.preventDefault();
          const targetPanel = tab.getAttribute("data-tab");

          // Update tab states
          tabs.forEach((t) => t.classList.remove("active"));
          tab.classList.add("active");

          // Update panel states
          panels.forEach((panel) => {
            if (panel.getAttribute("data-tab-panel") === targetPanel) {
              panel.classList.add("active");
            } else {
              panel.classList.remove("active");
            }
          });
        });
      });
    });
  },

  // Tooltip functionality
  initTooltips: function () {
    const tooltipElements = document.querySelectorAll("[data-tooltip]");
    tooltipElements.forEach((element) => {
      element.addEventListener("mouseenter", () => {
        this.showTooltip(element);
      });
      element.addEventListener("mouseleave", () => {
        this.hideTooltip(element);
      });
    });
  },

  showTooltip: function (element) {
    const text = element.getAttribute("data-tooltip");
    const tooltip = document.createElement("div");
    tooltip.className = "garden-tooltip";
    tooltip.textContent = text;
    tooltip.id = "tooltip-" + Date.now();

    document.body.appendChild(tooltip);

    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px";
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + "px";

    element.setAttribute("data-tooltip-id", tooltip.id);
  },

  hideTooltip: function (element) {
    const tooltipId = element.getAttribute("data-tooltip-id");
    if (tooltipId) {
      const tooltip = document.getElementById(tooltipId);
      if (tooltip) {
        tooltip.remove();
      }
      element.removeAttribute("data-tooltip-id");
    }
  },

  // Notification system
  initNotifications: function () {
    // Auto-dismiss notifications
    const notifications = document.querySelectorAll(".garden-notification[data-auto-dismiss]");
    notifications.forEach((notification) => {
      const delay = parseInt(notification.getAttribute("data-auto-dismiss")) || 5000;
      setTimeout(() => {
        this.hideNotification(notification);
      }, delay);
    });

    // Manual dismiss buttons
    const dismissButtons = document.querySelectorAll("[data-notification-dismiss]");
    dismissButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const notification = button.closest(".garden-notification");
        this.hideNotification(notification);
      });
    });
  },

  showNotification: function (message, type = "info", duration = 5000) {
    const notification = document.createElement("div");
    notification.className = `garden-notification notification-${type}`;
    notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-dismiss" data-notification-dismiss>&times;</button>
        `;

    const container =
      document.querySelector(".notification-container") || this.createNotificationContainer();
    container.appendChild(notification);

    // Auto dismiss
    if (duration > 0) {
      setTimeout(() => this.hideNotification(notification), duration);
    }

    return notification;
  },

  hideNotification: function (notification) {
    if (notification) {
      notification.style.opacity = "0";
      notification.style.transform = "translateX(100%)";
      setTimeout(() => notification.remove(), 300);
    }
  },

  createNotificationContainer: function () {
    const container = document.createElement("div");
    container.className = "notification-container";
    document.body.appendChild(container);
    return container;
  },

  // Utility functions
  utils: {
    // Format currency
    formatCurrency: function (amount, currency = "USD") {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currency,
      }).format(amount);
    },

    // Format percentage
    formatPercentage: function (value, decimals = 2) {
      return (value * 100).toFixed(decimals) + "%";
    },

    // Debounce function
    debounce: function (func, wait) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    },

    // Copy to clipboard
    copyToClipboard: function (text) {
      if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers
        const textArea = document.createElement("textarea");
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
        return Promise.resolve();
      }
    },
  },
};

// Initialize on DOM ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => GardenUI.init());
} else {
  GardenUI.init();
}

// Expose globally
window.GardenUI = GardenUI;
