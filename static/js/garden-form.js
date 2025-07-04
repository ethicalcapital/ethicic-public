/**
 * Garden UI Form Component JavaScript
 * Handles AJAX form submission, validation, and user feedback
 *
 * Usage:
 * <script src="/static/js/garden-form.js"></script>
 * <!-- Form HTML with data-ajax="true" -->
 * <script>GardenForm.init('form-id');</script>
 */

const GardenForm = {
  // Form instances
  forms: new Map(),

  /**
   * Initialize a form with AJAX capabilities
   * @param {string} formId - Form element ID
   * @param {Object} options - Configuration options
   */
  init (formId, options = {}) {
    const form = document.getElementById(formId);
    if (!form) {
      console.warn('GardenForm: Form not found:', formId);
      return;
    }

    const config = {
      ajax: form.dataset.ajax === 'true' || options.ajax,
      successCallback: options.onSuccess,
      errorCallback: options.onError,
      beforeSubmit: options.beforeSubmit,
      afterSubmit: options.afterSubmit,
      ...options
    };

    this.forms.set(formId, config);

    if (config.ajax) {
      this.setupAjaxForm(formId);
    }

    this.setupValidation(formId);
    console.log('GardenForm initialized:', formId);
  },

  /**
   * Setup AJAX form submission
   */
  setupAjaxForm (formId) {
    const form = document.getElementById(formId);
    const config = this.forms.get(formId);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      // Call beforeSubmit callback if provided
      if (config.beforeSubmit && config.beforeSubmit(form) === false) {
        return;
      }

      const formData = new FormData(form);
      const submitButton = form.querySelector('button[type="submit"]');
      const originalText = submitButton ? submitButton.innerHTML : '';

      try {
        // Show loading state
        this.setLoadingState(submitButton, true);

        const response = await fetch(form.action || window.location.href, {
          method: form.method,
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const data = await response.json();

        if (data.success) {
          this.handleSuccess(formId, data);
        } else {
          this.handleError(formId, data);
        }
      } catch (error) {
        console.error('Form submission error:', error);
        this.showMessage(formId, 'An error occurred. Please try again.', 'error');
      } finally {
        // Restore button state
        this.setLoadingState(submitButton, false, originalText);

        // Call afterSubmit callback if provided
        if (config.afterSubmit) {
          config.afterSubmit(form);
        }
      }
    });
  },

  /**
   * Handle successful form submission
   */
  handleSuccess (formId, data) {
    const form = document.getElementById(formId);
    const config = this.forms.get(formId);

    // Show success message
    if (data.message) {
      this.showMessage(formId, data.message, 'success');
    }

    // Handle redirect
    if (data.redirect) {
      setTimeout(() => {
        window.location.href = data.redirect;
      }, 1000);
    } else {
      // Reset form on success
      form.reset();
      this.clearErrors(formId);
    }

    // Call success callback if provided
    if (config.successCallback) {
      config.successCallback(data, form);
    }
  },

  /**
   * Handle form submission errors
   */
  handleError (formId, data) {
    const form = document.getElementById(formId);
    const config = this.forms.get(formId);

    // Display field errors
    if (data.errors) {
      this.displayFieldErrors(formId, data.errors);
    }

    // Show general error message
    if (data.message) {
      this.showMessage(formId, data.message, 'error');
    }

    // Call error callback if provided
    if (config.errorCallback) {
      config.errorCallback(data, form);
    }
  },

  /**
   * Set loading state for submit button
   */
  setLoadingState (button, loading, originalText = '') {
    if (!button) return;

    if (loading) {
      button.disabled = true;
      button.innerHTML = '<span class="loading-spinner"></span> SAVING...';
    } else {
      button.disabled = false;
      button.innerHTML = originalText;
    }
  },

  /**
   * Show form message
   */
  showMessage (formId, message, type) {
    const form = document.getElementById(formId);

    // Remove existing messages
    const existingMessage = form.querySelector('.form-message');
    if (existingMessage) {
      existingMessage.remove();
    }

    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `form-message form-message-${type}`;
    messageDiv.innerHTML = `
      <span class="message-icon">${type === 'success' ? '✓' : '⚠'}</span>
      <span class="message-text">${message}</span>
    `;

    // Insert at top of form
    form.insertBefore(messageDiv, form.firstChild);

    // Auto-remove success messages
    if (type === 'success') {
      setTimeout(() => {
        messageDiv.remove();
      }, 5000);
    }
  },

  /**
   * Display field-specific errors
   */
  displayFieldErrors (formId, errors) {
    const form = document.getElementById(formId);

    // Clear existing field errors
    this.clearErrors(formId);

    // Display new errors
    Object.keys(errors).forEach(fieldName => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (!field) return;

      const errorMessages = Array.isArray(errors[fieldName])
        ? errors[fieldName]
        : [errors[fieldName]];

      errorMessages.forEach(errorMessage => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = errorMessage;

        // Add error to field wrapper
        const fieldWrapper = field.closest('.garden-field-wrapper');
        if (fieldWrapper) {
          fieldWrapper.appendChild(errorDiv);
          fieldWrapper.classList.add('field-has-error');
        } else {
          // Fallback: add after field
          field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }

        // Add error class to field
        field.classList.add('error');
      });
    });
  },

  /**
   * Clear all form errors
   */
  clearErrors (formId) {
    const form = document.getElementById(formId);

    // Remove error elements
    form.querySelectorAll('.field-error').forEach(error => error.remove());

    // Remove error classes
    form.querySelectorAll('.error').forEach(element => {
      element.classList.remove('error');
    });

    form.querySelectorAll('.field-has-error').forEach(wrapper => {
      wrapper.classList.remove('field-has-error');
    });
  },

  /**
   * Setup basic client-side validation
   */
  setupValidation (formId) {
    const form = document.getElementById(formId);
    const fields = form.querySelectorAll('.garden-input');

    fields.forEach(field => {
      // Real-time validation on blur
      field.addEventListener('blur', () => {
        this.validateField(field);
      });

      // Clear errors on input
      field.addEventListener('input', () => {
        this.clearFieldError(field);
      });
    });
  },

  /**
   * Validate a single field
   */
  validateField (field) {
    const isValid = field.checkValidity();

    if (!isValid) {
      field.classList.add('error');

      // Show validation message if not already shown
      const wrapper = field.closest('.garden-field-wrapper');
      if (wrapper && !wrapper.querySelector('.field-error')) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = field.validationMessage;
        wrapper.appendChild(errorDiv);
        wrapper.classList.add('field-has-error');
      }
    }

    return isValid;
  },

  /**
   * Clear error for a specific field
   */
  clearFieldError (field) {
    field.classList.remove('error');

    const wrapper = field.closest('.garden-field-wrapper');
    if (wrapper) {
      const errors = wrapper.querySelectorAll('.field-error');
      errors.forEach(error => error.remove());
      wrapper.classList.remove('field-has-error');
    }
  },

  /**
   * Validate entire form
   */
  validateForm (formId) {
    const form = document.getElementById(formId);
    const fields = form.querySelectorAll('.garden-input');
    let isValid = true;

    fields.forEach(field => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });

    return isValid;
  },

  /**
   * Reset form and clear all errors
   */
  reset (formId) {
    const form = document.getElementById(formId);
    form.reset();
    this.clearErrors(formId);
  }
};

// Auto-initialize forms with data-auto-init attribute
document.addEventListener('DOMContentLoaded', () => {
  const autoForms = document.querySelectorAll('[data-auto-init="garden-form"]');
  autoForms.forEach(form => {
    const formId = form.id;
    const options = {
      ajax: form.dataset.ajax === 'true'
    };
    GardenForm.init(formId, options);
  });
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GardenForm;
}
