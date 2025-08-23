/**
 * Cross-Browser Compatibility JavaScript Fixes
 * Addresses Chrome vs Chromium rendering and behavior differences
 */

(function() {
    'use strict';
    
    // Browser detection
    const isChrome = navigator.userAgent.includes('Chrome');
    const isChromium = navigator.userAgent.includes('Chromium');
    const isWebKit = navigator.userAgent.includes('WebKit');
    
    console.log('Browser detected:', {
        isChrome,
        isChromium,
        isWebKit,
        userAgent: navigator.userAgent
    });
    
    // Font loading consistency
    function ensureFontLoading() {
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(function() {
                document.body.classList.add('fonts-loaded');
            });
        } else {
            // Fallback for older browsers
            setTimeout(function() {
                document.body.classList.add('fonts-loaded');
            }, 1000);
        }
    }
    
    // Flexbox gap fallback for older browsers
    function addFlexboxGapFallback() {
        const testElement = document.createElement('div');
        testElement.style.display = 'flex';
        testElement.style.gap = '10px';
        document.body.appendChild(testElement);
        
        const supportsGap = window.getComputedStyle(testElement).gap !== 'normal';
        document.body.removeChild(testElement);
        
        if (!supportsGap) {
            document.documentElement.classList.add('no-flexbox-gap');
            
            // Add margin-based spacing for navigation
            const navElements = document.querySelectorAll('nav.md\\:space-x-8 a');
            navElements.forEach(function(el, index) {
                if (index > 0) {
                    el.style.marginLeft = '2rem';
                }
            });
        }
    }
    
    // Smooth scrolling polyfill for older browsers
    function addSmoothScrolling() {
        if (!('scrollBehavior' in document.documentElement.style)) {
            // Add smooth scrolling polyfill if needed
            const links = document.querySelectorAll('a[href^="#"]');
            links.forEach(function(link) {
                link.addEventListener('click', function(e) {
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        }
    }
    
    // Fix backdrop-filter for older browsers
    function fixBackdropFilter() {
        const backdropElements = document.querySelectorAll('.backdrop-blur-sm');
        
        // Test backdrop-filter support
        const testDiv = document.createElement('div');
        testDiv.style.backdropFilter = 'blur(1px)';
        const supportsBackdropFilter = testDiv.style.backdropFilter !== '';
        
        if (!supportsBackdropFilter) {
            backdropElements.forEach(function(el) {
                el.style.backgroundColor = 'rgba(0, 0, 0, 0.75)';
                el.classList.add('backdrop-fallback');
            });
        }
    }
    
    // Navigation spacing fix specifically for Chrome/Chromium differences
    function fixNavigationSpacing() {
        const nav = document.querySelector('nav.md\\:space-x-8');
        if (nav) {
            // Force recalculation of spacing
            nav.style.display = 'none';
            nav.offsetHeight; // Trigger reflow
            nav.style.display = '';
            
            // Add explicit spacing to navigation items
            const navLinks = nav.querySelectorAll('a');
            navLinks.forEach(function(link, index) {
                if (index > 0) {
                    link.style.marginLeft = '2rem';
                }
            });
            
            // Responsive spacing for large screens
            function updateLargeScreenSpacing() {
                if (window.innerWidth >= 1024) {
                    navLinks.forEach(function(link, index) {
                        if (index > 0) {
                            link.style.marginLeft = '2.5rem';
                        }
                    });
                }
            }
            
            updateLargeScreenSpacing();
            window.addEventListener('resize', updateLargeScreenSpacing);
        }
    }
    
    // Performance chart compatibility
    function ensureChartCompatibility() {
        const chartContainers = document.querySelectorAll('[data-performance-chart]');
        chartContainers.forEach(function(container) {
            // Ensure Chart.js loads properly across browsers
            if (window.Chart) {
                // Chart.js is loaded, ensure proper initialization
                container.classList.add('chart-ready');
            }
        });
    }
    
    // Mobile menu touch events for better compatibility
    function improveMobileMenuCompatibility() {
        const mobileMenuButton = document.querySelector('[data-mobile-menu-button]');
        const mobileMenu = document.querySelector('[data-mobile-menu]');
        
        if (mobileMenuButton && mobileMenu) {
            // Add touch event listeners for better mobile compatibility
            mobileMenuButton.addEventListener('touchstart', function(e) {
                e.preventDefault();
                mobileMenuButton.click();
            }, { passive: false });
        }
    }
    
    // Initialize all compatibility fixes
    function initBrowserCompatibility() {
        ensureFontLoading();
        addFlexboxGapFallback();
        addSmoothScrolling();
        fixBackdropFilter();
        fixNavigationSpacing();
        ensureChartCompatibility();
        improveMobileMenuCompatibility();
        
        // Add browser-specific class to body
        if (isChrome && !isChromium) {
            document.body.classList.add('browser-chrome');
        } else if (isChromium) {
            document.body.classList.add('browser-chromium');
        }
        
        console.log('Cross-browser compatibility fixes initialized');
    }
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBrowserCompatibility);
    } else {
        initBrowserCompatibility();
    }
    
    // Re-run fixes on dynamic content changes (for SPA-like behavior)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                fixNavigationSpacing();
                ensureChartCompatibility();
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
})();