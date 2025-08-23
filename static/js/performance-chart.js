/**
 * Performance Chart Component for Investment Visualization
 * Creates interactive "Growth of $10,000" charts using Chart.js
 * Shows cumulative investment performance vs benchmark over time
 */

class PerformanceChart {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.chart = null;
        this.isLoading = false;
        
        // Default options
        this.options = {
            apiEndpoint: '/api/performance-chart/',
            defaultStrategy: 'growth',
            height: 400,
            responsive: true,
            showLegend: true,
            showTooltips: true,
            animationDuration: 750,
            ...options
        };
        
        // Bind methods
        this.init = this.init.bind(this);
        this.loadChart = this.loadChart.bind(this);
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
        this.showError = this.showError.bind(this);
        this.showLoading = this.showLoading.bind(this);
        
        // Initialize if container exists
        if (this.container) {
            this.init();
        }
    }
    
    init() {
        // Create container structure
        this.createContainerStructure();
        
        // Load Chart.js if not already loaded
        this.loadChartJS().then(() => {
            this.loadChart(this.options.defaultStrategy);
        });
    }
    
    createContainerStructure() {
        this.container.innerHTML = `
            <div class="performance-chart-wrapper relative">
                <div class="chart-header mb-6">
                    <h3 class="text-xl font-bold text-white mb-2">Growth of $10,000 Investment</h3>
                    <p class="text-sm text-gray-300 mb-4">Cumulative performance vs S&P 500 benchmark</p>
                    <div class="strategy-selector flex flex-wrap gap-2 mb-4">
                        <button class="strategy-btn px-3 py-1 text-xs bg-purple-800 text-white rounded hover:bg-purple-700 transition-colors" 
                                data-strategy="growth">Growth Strategy</button>
                        <button class="strategy-btn px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500 transition-colors" 
                                data-strategy="income">Income Strategy</button>
                        <button class="strategy-btn px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500 transition-colors" 
                                data-strategy="diversification">Diversification Strategy</button>
                    </div>
                </div>
                <div class="chart-loading hidden text-center py-8">
                    <div class="inline-flex items-center px-4 py-2 bg-purple-900 rounded-lg">
                        <div class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                        <span class="text-white text-sm">Loading performance data...</span>
                    </div>
                </div>
                <div class="chart-error hidden text-center py-8">
                    <div class="bg-red-900 border border-red-700 rounded-lg p-4">
                        <p class="text-red-200 text-sm">Unable to load performance data. Please try again later.</p>
                    </div>
                </div>
                <div class="chart-container" style="height: ${this.options.height}px;">
                    <canvas id="${this.containerId}-canvas"></canvas>
                </div>
                <div class="performance-summary hidden mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="summary-item bg-gray-800 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold text-green-400 strategy-final-value">-</div>
                        <div class="text-xs text-gray-300">Strategy Value</div>
                    </div>
                    <div class="summary-item bg-gray-800 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold text-gray-400 benchmark-final-value">-</div>
                        <div class="text-xs text-gray-300">Benchmark Value</div>
                    </div>
                    <div class="summary-item bg-gray-800 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold text-blue-400 outperformance-value">-</div>
                        <div class="text-xs text-gray-300">Outperformance</div>
                    </div>
                    <div class="summary-item bg-gray-800 rounded-lg p-3 text-center">
                        <div class="text-lg font-bold text-purple-400 total-return-value">-</div>
                        <div class="text-xs text-gray-300">Total Return</div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners for strategy selector
        this.container.querySelectorAll('.strategy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const strategy = e.target.dataset.strategy;
                this.loadChart(strategy);
                
                // Update button states
                this.container.querySelectorAll('.strategy-btn').forEach(b => {
                    b.classList.remove('bg-purple-800');
                    b.classList.add('bg-gray-600');
                });
                e.target.classList.remove('bg-gray-600');
                e.target.classList.add('bg-purple-800');
            });
        });
    }
    
    async loadChartJS() {
        if (window.Chart) {
            return Promise.resolve();
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
    
    async loadChart(strategy = 'growth') {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const url = `${this.options.apiEndpoint}?strategy=${encodeURIComponent(strategy)}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.createChart(data);
            this.updateSummary(data.performance_summary, data.strategy_name);
            
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showError(error.message);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    createChart(data) {
        const canvas = document.getElementById(`${this.containerId}-canvas`);
        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Create new chart
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: false
                    },
                    legend: {
                        display: this.options.showLegend,
                        position: 'bottom',
                        labels: {
                            color: '#D1D5DB',
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        enabled: this.options.showTooltips,
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(17, 24, 39, 0.95)',
                        titleColor: '#F9FAFB',
                        bodyColor: '#E5E7EB',
                        borderColor: '#6B7280',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        displayColors: true,
                        callbacks: {
                            title: function(tooltipItems) {
                                return tooltipItems[0].label;
                            },
                            label: function(context) {
                                const value = context.parsed.y;
                                const formatted = new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(value);
                                return `${context.dataset.label}: ${formatted}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time Period',
                            color: '#9CA3AF',
                            font: {
                                size: 11
                            }
                        },
                        ticks: {
                            color: '#9CA3AF',
                            maxTicksLimit: 8,
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)',
                            drawBorder: false
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Investment Value ($)',
                            color: '#9CA3AF',
                            font: {
                                size: 11
                            }
                        },
                        ticks: {
                            color: '#9CA3AF',
                            callback: function(value) {
                                return new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0
                                }).format(value);
                            },
                            font: {
                                size: 10
                            }
                        },
                        grid: {
                            color: 'rgba(75, 85, 99, 0.3)',
                            drawBorder: false
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                elements: {
                    point: {
                        hoverRadius: 8
                    }
                },
                animation: {
                    duration: this.options.animationDuration,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }
    
    updateSummary(summary, strategyName) {
        if (!summary) return;
        
        const summaryContainer = this.container.querySelector('.performance-summary');
        
        // Format currency values
        const formatCurrency = (value) => {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(value);
        };
        
        const formatPercent = (value) => {
            const sign = value >= 0 ? '+' : '';
            return `${sign}${value.toFixed(1)}%`;
        };
        
        // Update values
        summaryContainer.querySelector('.strategy-final-value').textContent = formatCurrency(summary.final_strategy_value);
        summaryContainer.querySelector('.benchmark-final-value').textContent = formatCurrency(summary.final_benchmark_value);
        summaryContainer.querySelector('.outperformance-value').textContent = formatCurrency(summary.outperformance);
        summaryContainer.querySelector('.total-return-value').textContent = formatPercent(summary.strategy_total_return);
        
        // Show summary
        summaryContainer.classList.remove('hidden');
        
        // Update header with strategy name
        const header = this.container.querySelector('.chart-header h3');
        if (header && strategyName) {
            header.textContent = `Growth of $10,000: ${strategyName} Strategy`;
        }
    }
    
    showLoading() {
        this.container.querySelector('.chart-loading').classList.remove('hidden');
        this.container.querySelector('.chart-error').classList.add('hidden');
        this.container.querySelector('.performance-summary').classList.add('hidden');
    }
    
    hideLoading() {
        this.container.querySelector('.chart-loading').classList.add('hidden');
    }
    
    showError(message = 'Unable to load chart data') {
        const errorContainer = this.container.querySelector('.chart-error');
        errorContainer.querySelector('p').textContent = message;
        errorContainer.classList.remove('hidden');
        this.container.querySelector('.chart-loading').classList.add('hidden');
        this.container.querySelector('.performance-summary').classList.add('hidden');
    }
    
    // Public methods for external control
    updateChart(strategy) {
        this.loadChart(strategy);
    }
    
    destroy() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

// Auto-initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all performance charts found on page
    document.querySelectorAll('[data-performance-chart]').forEach(container => {
        const options = {
            defaultStrategy: container.dataset.defaultStrategy || 'growth',
            height: parseInt(container.dataset.height) || 400
        };
        
        new PerformanceChart(container.id, options);
    });
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceChart;
}