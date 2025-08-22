/**
 * Test PostHog Error Tracking
 * This file contains functions to test error tracking in development
 */

// Test regular JavaScript error
function testJavaScriptError() {
    console.log('Testing JavaScript error...');
    // This will throw a TypeError
    const obj = null;
    obj.nonExistentMethod();
}

// Test unhandled promise rejection
function testPromiseRejection() {
    console.log('Testing promise rejection...');
    new Promise((resolve, reject) => {
        reject(new Error('Test promise rejection for PostHog'));
    });
}

// Test manual exception capture
function testManualException() {
    console.log('Testing manual exception capture...');
    try {
        // Intentionally cause an error
        JSON.parse('invalid json');
    } catch (error) {
        if (window.posthog) {
            // Use the $exception event format
            window.posthog.capture('$exception', {
                $exception_type: error.name,
                $exception_message: error.message,
                $exception_personURL: window.location.href,
                $exception_list: [{
                    type: error.name,
                    value: error.message,
                    stacktrace: {
                        frames: error.stack ? error.stack.split('\n').map(line => ({
                            raw: line
                        })) : []
                    }
                }],
                $exception_stack_trace_raw: error.stack,
                manual_capture: true,
                test_error: true
            });
            console.log('Manual exception captured and sent to PostHog');
        } else {
            console.error('PostHog not available');
        }
    }
}

// Add test buttons to the page (only in development)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    document.addEventListener('DOMContentLoaded', function() {
        const testDiv = document.createElement('div');
        testDiv.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #333; padding: 10px; border-radius: 8px; z-index: 9999;';
        testDiv.innerHTML = `
            <p style="color: white; margin: 0 0 10px 0; font-size: 12px;">PostHog Error Testing</p>
            <button onclick="testJavaScriptError()" style="display: block; margin: 5px 0; padding: 5px 10px; font-size: 12px;">Test JS Error</button>
            <button onclick="testPromiseRejection()" style="display: block; margin: 5px 0; padding: 5px 10px; font-size: 12px;">Test Promise Rejection</button>
            <button onclick="testManualException()" style="display: block; margin: 5px 0; padding: 5px 10px; font-size: 12px;">Test Manual Exception</button>
        `;
        document.body.appendChild(testDiv);
    });
}