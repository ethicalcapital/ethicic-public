/**
 * Garden Terminal Theme Toggle System
 * Robust implementation with fallbacks and debugging
 */

(function () {
  'use strict'

  // Theme configuration
  const THEMES = ['auto', 'light', 'dark']
  const THEME_ICONS = {
    auto: '🌓',
    light: '☀️',
    dark: '🌙'
  }

  // State management
  let currentTheme = 'auto'
  let isInitialized = false

  // Debug logging - enabled by default for troubleshooting
  function debugLog (message, data = null) {
    if (window.gardenDebug || true) { // Always log for now
      console.log(`[GARDEN THEME] ${message}`, data || '')
    }
  }

  // Calculate milliseconds until a specific hour today or tomorrow
  function getTimeUntilHour (targetHour) {
    const now = new Date()
    const target = new Date()
    target.setHours(targetHour, 0, 0, 0)

    // If target time has passed today, set for tomorrow
    if (target <= now) {
      target.setDate(target.getDate() + 1)
    }

    return target.getTime() - now.getTime()
  }

  // Get effective theme (resolve 'auto' to actual theme based on system preference and time)
  function getEffectiveTheme (theme) {
    if (theme === 'auto') {
      // First, check system preference
      const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches

      // Get user's local time
      const now = new Date()
      const hour = now.getHours()

      // Light theme during day hours (6 AM to 8 PM), dark theme at night
      const isDayTime = hour >= 6 && hour < 20
      const timeBasedTheme = isDayTime ? 'light' : 'dark'

      // Prefer system setting, but fall back to time-based if no system preference
      let autoTheme
      if (window.matchMedia) {
        autoTheme = systemPrefersDark ? 'dark' : 'light'
        debugLog(`System-based theme calculation: systemPrefersDark=${systemPrefersDark}, theme=${autoTheme}`)
      } else {
        autoTheme = timeBasedTheme
        debugLog(`Time-based theme calculation (no system support): hour=${hour}, isDayTime=${isDayTime}, theme=${autoTheme}`)
      }

      return autoTheme
    }
    return theme
  }

  // Apply theme to DOM
  function applyTheme (theme) {
    debugLog(`Applying theme: ${theme}`)

    const htmlElement = document.documentElement
    const effectiveTheme = getEffectiveTheme(theme)

    // Update data-theme attribute
    htmlElement.setAttribute('data-theme', effectiveTheme)

    // Update icon
    const iconElement = document.getElementById('theme-icon')
    if (iconElement) {
      iconElement.textContent = THEME_ICONS[theme] || '🌓'
      debugLog(`Icon updated to: ${THEME_ICONS[theme]}`)
    }

    // Store in localStorage
    try {
      localStorage.setItem('garden-theme', theme)
      debugLog(`Theme saved to localStorage: ${theme}`)
    } catch (e) {
      debugLog(`localStorage error: ${e.message}`)
    }

    // Update global state
    currentTheme = theme

    debugLog(`Theme applied successfully. Current: ${theme}, Effective: ${effectiveTheme}`)

    return effectiveTheme
  }

  // Save theme to server
  function saveThemeToServer (theme) {
    debugLog(`Saving theme to server: ${theme}`)

    // Get CSRF token from cookie or meta tag
    function getCSRFToken () {
      // Try to get from meta tag first
      const metaTag = document.querySelector('meta[name="csrf-token"]')
      if (metaTag) {
        return metaTag.getAttribute('content')
      }

      // Try to get from cookie
      const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))

      return cookieValue ? cookieValue.split('=')[1] : null
    }

    const csrfToken = getCSRFToken()
    const headers = {
      'Content-Type': 'application/json'
    }

    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }

    const requestData = {
      method: 'POST',
      headers,
      body: JSON.stringify({ theme })
    }

    fetch('/platform/auth/api/theme/set/', requestData)
      .then(response => {
        debugLog(`Server response status: ${response.status}`)
        if (!response.ok) {
          return response.text().then(text => {
            throw new Error(`HTTP ${response.status}: ${text}`)
          })
        }
        return response.json()
      })
      .then(data => {
        debugLog('Server save successful:', data)
      })
      .catch(error => {
        debugLog('Server save failed:', error)
        console.error('Theme save error details:', error)
      })
  }

  // Set theme (main function)
  function setTheme (theme) {
    debugLog(`Setting theme to: ${theme}`)

    if (!THEMES.includes(theme)) {
      debugLog(`Invalid theme: ${theme}. Valid themes: ${THEMES.join(', ')}`)
      return
    }

    // Apply immediately
    const effectiveTheme = applyTheme(theme)

    // Save to server (async)
    saveThemeToServer(theme)

    // Dispatch custom event
    try {
      const event = new CustomEvent('gardenThemeChanged', {
        detail: { theme, effectiveTheme }
      })
      document.dispatchEvent(event)
      debugLog('Custom event dispatched: gardenThemeChanged')
    } catch (e) {
      debugLog(`Event dispatch error: ${e.message}`)
    }

    return effectiveTheme
  }

  // Cycle to next theme
  function cycleTheme () {
    debugLog(`Cycling theme from: ${currentTheme}`)

    const currentIndex = THEMES.indexOf(currentTheme)
    const nextIndex = (currentIndex + 1) % THEMES.length
    const nextTheme = THEMES[nextIndex]

    debugLog(`Cycling to: ${nextTheme} (index: ${nextIndex})`)

    return setTheme(nextTheme)
  }

  // Initialize theme system
  function initializeTheme () {
    if (isInitialized) {
      debugLog('Theme system already initialized')
      return
    }

    debugLog('Initializing theme system...')

    // Get initial theme from various sources (priority order)
    let initialTheme = 'auto'

    // 1. Check URL parameter
    const urlParams = new URLSearchParams(window.location.search)
    const urlTheme = urlParams.get('theme')
    if (urlTheme && THEMES.includes(urlTheme)) {
      initialTheme = urlTheme
      debugLog(`Theme from URL: ${initialTheme}`)
    }
    // 2. Check template variable
    else if (window.gardenInitialTheme && THEMES.includes(window.gardenInitialTheme)) {
      initialTheme = window.gardenInitialTheme
      debugLog(`Theme from template: ${initialTheme}`)
    }
    // 3. Check localStorage
    else {
      try {
        const storedTheme = localStorage.getItem('garden-theme')
        if (storedTheme && THEMES.includes(storedTheme)) {
          initialTheme = storedTheme
          debugLog(`Theme from localStorage: ${initialTheme}`)
        }
      } catch (e) {
        debugLog(`localStorage read error: ${e.message}`)
      }
    }

    // Apply initial theme
    applyTheme(initialTheme)

    // Set up theme toggle button
    const toggleButton = document.getElementById('theme-toggle')
    if (toggleButton) {
      debugLog('Theme toggle button found, attaching event listener')

      // Remove any existing listeners by cloning the button
      const newButton = toggleButton.cloneNode(true)
      toggleButton.parentNode.replaceChild(newButton, toggleButton)

      // Add click listener
      newButton.addEventListener('click', function (e) {
        e.preventDefault()
        debugLog('Theme toggle button clicked')
        cycleTheme()
      })

      // Add keyboard support
      newButton.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          debugLog('Theme toggle button activated via keyboard')
          cycleTheme()
        }
      })

      debugLog('Theme toggle button event listeners attached')
    } else {
      debugLog('Theme toggle button not found')
    }

    // Set up system and time-based theme updates for auto mode
    try {
      // Listen for system theme changes
      if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        mediaQuery.addEventListener('change', function () {
          if (currentTheme === 'auto') {
            debugLog('System theme preference changed, updating auto theme')
            applyTheme('auto')
          }
        })
        debugLog('System theme change listener added')
      }

      // Check for theme changes every hour when in auto mode (fallback for time-based)
      setInterval(function () {
        if (currentTheme === 'auto') {
          debugLog('Hourly time check, updating auto theme')
          applyTheme('auto')
        }
      }, 60 * 60 * 1000) // Check every hour

      // Also check at the start of each day (light/dark transition times) - only used as fallback
      const now = new Date()
      const msUntilNext6AM = getTimeUntilHour(6)
      const msUntilNext8PM = getTimeUntilHour(20)

      setTimeout(function () {
        if (currentTheme === 'auto') {
          debugLog('6 AM transition, updating auto theme')
          applyTheme('auto')
        }
      }, msUntilNext6AM)

      setTimeout(function () {
        if (currentTheme === 'auto') {
          debugLog('8 PM transition, updating auto theme')
          applyTheme('auto')
        }
      }, msUntilNext8PM)

      debugLog('Theme change listeners added')
    } catch (e) {
      debugLog(`Theme listener error: ${e.message}`)
    }

    // Add keyboard shortcut (Ctrl+Shift+T)
    document.addEventListener('keydown', function (e) {
      if (e.ctrlKey && e.shiftKey && e.key === 'T') {
        e.preventDefault()
        debugLog('Keyboard shortcut activated: Ctrl+Shift+T')
        cycleTheme()
      }
    })

    isInitialized = true
    debugLog('Theme system initialization complete')
  }

  // Wait for DOM to be ready
  function whenReady (callback) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback)
    } else {
      callback()
    }
  }

  // Public API
  window.GardenTheme = {
    setTheme,
    cycleTheme,
    getCurrentTheme: () => currentTheme,
    getEffectiveTheme: () => getEffectiveTheme(currentTheme),
    enableDebug: () => { window.gardenDebug = true },
    disableDebug: () => { window.gardenDebug = false }
  }

  // Auto-initialize when DOM is ready
  whenReady(initializeTheme)

  // Also initialize immediately if DOM is already ready
  if (document.readyState !== 'loading') {
    setTimeout(initializeTheme, 0)
  }

  debugLog('Theme toggle script loaded')
})()
