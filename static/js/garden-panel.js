/**
 * Garden UI Panel Component JavaScript
 * Handles collapsible panels and panel interactions
 *
 * Usage:
 * <script src="/static/js/garden-panel.js"></script>
 * <!-- Panel HTML with data-collapsible="true" -->
 * <script>GardenPanel.init('panel-id');</script>
 */

const GardenPanel = {
  // Panel instances
  panels: new Map(),

  /**
   * Initialize a panel with interactive functionality
   * @param {string} panelId - Panel element ID
   * @param {Object} options - Configuration options
   */
  init(panelId, options = {}) {
    const panel = document.getElementById(panelId);
    if (!panel) {
      console.warn("GardenPanel: Panel not found:", panelId);
      return;
    }

    const config = {
      collapsible: panel.dataset.collapsible === "true" || options.collapsible,
      startCollapsed: options.startCollapsed || false,
      animationDuration: options.animationDuration || 200,
      onToggle: options.onToggle,
      onExpand: options.onExpand,
      onCollapse: options.onCollapse,
      ...options,
    };

    this.panels.set(panelId, config);

    if (config.collapsible) {
      this.setupCollapsible(panelId);
    }

    // Set initial state
    if (config.startCollapsed) {
      this.collapse(panelId, false); // No animation on init
    }

    // GardenPanel initialized
  },

  /**
   * Setup collapsible functionality
   */
  setupCollapsible(panelId) {
    const panel = document.getElementById(panelId);
    const collapseBtn = panel.querySelector(".panel-collapse-btn");

    if (!collapseBtn) {
      console.warn("GardenPanel: No collapse button found for", panelId);
      return;
    }

    collapseBtn.addEventListener("click", (e) => {
      e.preventDefault();
      this.toggle(panelId);
    });

    // Make header clickable if specified
    const config = this.panels.get(panelId);
    if (config.headerClickable) {
      const header = panel.querySelector(".garden-panel-header");
      if (header) {
        header.style.cursor = "pointer";
        header.addEventListener("click", (e) => {
          // Don't trigger if clicking on buttons
          if (!e.target.closest("button")) {
            this.toggle(panelId);
          }
        });
      }
    }
  },

  /**
   * Toggle panel collapsed state
   */
  toggle(panelId, animate = true) {
    const panel = document.getElementById(panelId);
    const content = panel.querySelector(".garden-panel-content");

    if (!content) return;

    const isCollapsed = content.style.display === "none" || content.classList.contains("collapsed");

    if (isCollapsed) {
      this.expand(panelId, animate);
    } else {
      this.collapse(panelId, animate);
    }
  },

  /**
   * Expand panel
   */
  expand(panelId, animate = true) {
    const panel = document.getElementById(panelId);
    const content = panel.querySelector(".garden-panel-content");
    const icon = panel.querySelector(".collapse-icon");
    const config = this.panels.get(panelId);

    if (!content) return;

    if (animate && config.animationDuration > 0) {
      // Smooth animation
      content.style.height = "0px";
      content.style.overflow = "hidden";
      content.style.display = "block";

      // Force reflow
      void content.offsetHeight;

      content.style.transition = `height ${config.animationDuration}ms ease`;
      content.style.height = content.scrollHeight + "px";

      setTimeout(() => {
        content.style.height = "";
        content.style.overflow = "";
        content.style.transition = "";
      }, config.animationDuration);
    } else {
      content.style.display = "block";
    }

    content.classList.remove("collapsed");
    panel.classList.remove("panel-collapsed");

    // Update icon
    if (icon) {
      icon.textContent = "▼";
    }

    // Call callbacks
    if (config.onExpand) {
      config.onExpand(panelId, panel);
    }
    if (config.onToggle) {
      config.onToggle(panelId, panel, false);
    }
  },

  /**
   * Collapse panel
   */
  collapse(panelId, animate = true) {
    const panel = document.getElementById(panelId);
    const content = panel.querySelector(".garden-panel-content");
    const icon = panel.querySelector(".collapse-icon");
    const config = this.panels.get(panelId);

    if (!content) return;

    if (animate && config.animationDuration > 0) {
      // Smooth animation
      content.style.height = content.scrollHeight + "px";
      content.style.overflow = "hidden";
      content.style.transition = `height ${config.animationDuration}ms ease`;

      // Force reflow
      void content.offsetHeight;

      content.style.height = "0px";

      setTimeout(() => {
        content.style.display = "none";
        content.style.height = "";
        content.style.overflow = "";
        content.style.transition = "";
      }, config.animationDuration);
    } else {
      content.style.display = "none";
    }

    content.classList.add("collapsed");
    panel.classList.add("panel-collapsed");

    // Update icon
    if (icon) {
      icon.textContent = "▶";
    }

    // Call callbacks
    if (config.onCollapse) {
      config.onCollapse(panelId, panel);
    }
    if (config.onToggle) {
      config.onToggle(panelId, panel, true);
    }
  },

  /**
   * Check if panel is collapsed
   */
  isCollapsed(panelId) {
    const panel = document.getElementById(panelId);
    const content = panel.querySelector(".garden-panel-content");

    return content && (content.style.display === "none" || content.classList.contains("collapsed"));
  },

  /**
   * Set panel loading state
   */
  setLoading(panelId, loading = true) {
    const panel = document.getElementById(panelId);
    const content = panel.querySelector(".garden-panel-content");
    const loadingDiv = panel.querySelector(".panel-loading");

    if (loading) {
      if (content) content.style.display = "none";

      if (!loadingDiv) {
        const loading = document.createElement("div");
        loading.className = "panel-loading";
        loading.innerHTML = `
          <div class="loading-spinner"></div>
          <div class="loading-text">Loading...</div>
        `;
        panel.appendChild(loading);
      } else {
        loadingDiv.style.display = "block";
      }
    } else {
      if (content) content.style.display = "block";
      if (loadingDiv) loadingDiv.style.display = "none";
    }
  },

  /**
   * Update panel status
   */
  setStatus(panelId, status) {
    const panel = document.getElementById(panelId);

    // Remove existing status classes
    panel.classList.remove("status-success", "status-warning", "status-error", "status-info");

    // Add new status
    if (status) {
      panel.classList.add(`status-${status}`);
      panel.dataset.status = status;
    }
  },

  /**
   * Update panel title
   */
  setTitle(panelId, title) {
    const panel = document.getElementById(panelId);
    const titleElement = panel.querySelector(".panel-title");

    if (titleElement) {
      titleElement.textContent = title.toUpperCase();
    }
  },

  /**
   * Update panel count badge
   */
  setCount(panelId, count) {
    const panel = document.getElementById(panelId);
    let countBadge = panel.querySelector(".panel-count");

    if (count !== null && count !== undefined) {
      if (!countBadge) {
        countBadge = document.createElement("span");
        countBadge.className = "garden-badge panel-count";

        const headerLeft = panel.querySelector(".panel-header-left");
        if (headerLeft) {
          headerLeft.appendChild(countBadge);
        }
      }
      countBadge.textContent = count;
      countBadge.style.display = "";
    } else if (countBadge) {
      countBadge.style.display = "none";
    }
  },

  /**
   * Refresh panel content (if refresh function provided)
   */
  refresh(panelId) {
    const config = this.panels.get(panelId);

    if (config && config.refreshCallback) {
      this.setLoading(panelId, true);

      Promise.resolve(config.refreshCallback(panelId))
        .then(() => {
          this.setLoading(panelId, false);
        })
        .catch((error) => {
          console.error("Panel refresh error:", error);
          this.setLoading(panelId, false);
          this.setStatus(panelId, "error");
        });
    }
  },
};

// Global function for backwards compatibility
window.togglePanel = function (panelId) {
  GardenPanel.toggle(panelId);
};

// Auto-initialize panels with data-auto-init attribute
document.addEventListener("DOMContentLoaded", () => {
  const autoPanels = document.querySelectorAll('[data-auto-init="garden-panel"]');
  autoPanels.forEach((panel) => {
    const panelId = panel.id;
    const options = {
      collapsible: panel.dataset.collapsible === "true",
      startCollapsed: panel.dataset.startCollapsed === "true",
      headerClickable: panel.dataset.headerClickable === "true",
    };
    GardenPanel.init(panelId, options);
  });
});

// Export for module use
if (typeof module !== "undefined" && module.exports) {
  module.exports = GardenPanel;
}
