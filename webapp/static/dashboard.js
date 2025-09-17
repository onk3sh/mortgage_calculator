// Dashboard JavaScript for Mortgage Calculator
let currentData = null;
let charts = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
});

function showStatus(message, type = 'loading') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
}

function hideStatus() {
    document.getElementById('status').style.display = 'none';
}

// Combined function to run and load scenario
async function runAndLoadScenario(scenario) {
    showStatus(`Running ${scenario} scenario...`, 'loading');

    // Update active button
    document.querySelectorAll('.scenario-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    try {
        const response = await fetch(`/run_scenario/${scenario}`, {
            method: 'POST'
        });

        if (response.ok) {
            showStatus(`${scenario} scenario completed successfully!`, 'success');
            setTimeout(() => {
                loadScenario(scenario);
            }, 1000);
        } else {
            showStatus(`Error running ${scenario} scenario`, 'error');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

// Legacy function - keeping for compatibility
async function runScenario(scenario) {
    return runAndLoadScenario(scenario);
}

// Load scenario data
async function loadScenario(scenario) {
    showStatus(`Loading ${scenario} scenario data...`, 'loading');

    try {
        const [summaryResponse, detailsResponse] = await Promise.all([
            fetch(`/data/${scenario}/summary`),
            fetch(`/data/${scenario}/details`)
        ]);

        if (summaryResponse.ok && detailsResponse.ok) {
            const summaryResponseData = await summaryResponse.json();
            const detailsData = await detailsResponse.json();

            // Handle both old format (array) and new format (object with summary and homeValueData)
            let summaryData, homeValueData;

            if (Array.isArray(summaryResponseData)) {
                // Old format - array of summary data
                summaryData = summaryResponseData;
                homeValueData = null;
            } else {
                // New format - object with summary and homeValueData
                summaryData = summaryResponseData.summary;
                homeValueData = summaryResponseData.homeValueData;
            }

            currentData = {
                scenario: scenario,
                summary: summaryData,
                details: detailsData,
                homeValueData: homeValueData
            };

            updateDashboard();
            showStatus(`${scenario} scenario loaded successfully!`, 'success');
            setTimeout(hideStatus, 2000);
        } else {
            showStatus(`Error loading ${scenario} data`, 'error');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

function updateDashboard() {
    if (!currentData) return;

    updateSummaryTable();
    updateCharts();
    updateAnalysis();

    // Also update additional charts with default views
    updateBalanceChart();
    updateHomeValueChart();
}

function updateSummaryTable() {
    const content = document.getElementById('summary-content');
    const summary = currentData.summary;

    if (!summary || !Array.isArray(summary)) {
        content.innerHTML = '<div class="error">Error: Invalid summary data format</div>';
        return;
    }

    let bestEquity = '';
    let bestInterest = '';
    let maxEquity = 0;
    let minInterest = Infinity;

    // Find best performers
    summary.forEach(row => {
        if (row['Equity Built (%)'] > maxEquity) {
            maxEquity = row['Equity Built (%)'];
            bestEquity = row['Strategy'];
        }
        if (row['Total Interest'] < minInterest) {
            minInterest = row['Total Interest'];
            bestInterest = row['Strategy'];
        }
    });

    let html = `
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Strategy</th>
                    <th>Total Payments</th>
                    <th>Total Interest</th>
                    <th>Equity Built</th>
                    <th>Avg Rate</th>
                </tr>
            </thead>
            <tbody>
    `;

    summary.forEach(row => {
        const isBestEquity = row['Strategy'] === bestEquity;
        const isBestInterest = row['Strategy'] === bestInterest;
        const rowClass = (isBestEquity || isBestInterest) ? 'best-strategy' : '';

        html += `
            <tr class="${rowClass}">
                <td>${row['Strategy']}</td>
                <td>$${Math.round(row['Total Payments']).toLocaleString()}</td>
                <td>$${Math.round(row['Total Interest']).toLocaleString()}</td>
                <td>${row['Equity Built (%)'].toFixed(2)}%</td>
                <td>${row['Average Rate (%)'].toFixed(2)}%</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    content.innerHTML = html;
}

function initializeCharts() {
    // Register Chart.js plugins
    Chart.register(ChartZoom);

    // Rate progression chart
    const rateCtx = document.getElementById('rateChart').getContext('2d');
    charts.rate = new Chart(rateCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Interest Rate (%)'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Rate Progression Over Time'
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}%`;
                        }
                    }
                },
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'x',
                    },
                    pan: {
                        enabled: true,
                        mode: 'x',
                    }
                }
            }
        }
    });

    // Payment comparison chart
    const paymentCtx = document.getElementById('paymentChart').getContext('2d');
    charts.payment = new Chart(paymentCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Payments',
                data: [],
                backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
                borderColor: ['#0056b3', '#1e7e34', '#e0a800', '#bd2130'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Financial Comparison by Strategy'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });

    // Balance progression chart
    const balanceCtx = document.getElementById('balanceChart').getContext('2d');
    charts.balance = new Chart(balanceCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Balance ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Balance Progression Over Time'
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                },
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'xy',
                    },
                    pan: {
                        enabled: true,
                        mode: 'xy',
                    }
                }
            }
        }
    });

    // Equity chart
    const equityCtx = document.getElementById('equityChart').getContext('2d');
    charts.equity = new Chart(equityCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Equity Built by Strategy (%)'
                }
            }
        }
    });

    // Home Value chart
    const homeValueCtx = document.getElementById('homeValueChart').getContext('2d');
    charts.homeValue = new Chart(homeValueCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Net Cash on Sale',
                data: [],
                backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
                borderColor: ['#0056b3', '#1e7e34', '#e0a800', '#bd2130'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amount ($)'
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + (value / 1000).toFixed(0) + 'K';
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Net Cash on Sale by Strategy'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            }
        }
    });
}

function updateCharts() {
    if (!currentData) return;

    const summary = currentData.summary;
    const details = currentData.details;

    // Update payment comparison chart
    const strategies = summary.map(row => row['Strategy']);
    const payments = summary.map(row => row['Total Payments']);

    charts.payment.data.labels = strategies;
    charts.payment.data.datasets[0].data = payments;
    charts.payment.update();

    // Update equity chart
    const equity = summary.map(row => row['Equity Built (%)']);
    charts.equity.data.labels = strategies;
    charts.equity.data.datasets[0].data = equity;
    charts.equity.update();

    // Update rate progression chart (variable strategies only)
    if (details && details.length > 0) {
        const variableData = details.filter(row =>
            row.Strategy === 'Variable (Fixed Payment)' ||
            row.Strategy === 'Variable (Recalc Payment)'
        );

        if (variableData.length > 0) {
            // Group by strategy
            const strategies = ['Variable (Fixed Payment)', 'Variable (Recalc Payment)'];
            const datasets = [];

            strategies.forEach((strategy, index) => {
                const strategyData = variableData.filter(row => row.Strategy === strategy);
                if (strategyData.length > 0) {
                    datasets.push({
                        label: strategy,
                        data: strategyData.map(row => row.Rate),
                        borderColor: index === 0 ? '#007bff' : '#28a745',
                        backgroundColor: index === 0 ? '#007bff20' : '#28a74520',
                        fill: false,
                        tension: 0.1
                    });
                }
            });

            const months = variableData
                .filter(row => row.Strategy === strategies[0])
                .map(row => row.Month);

            charts.rate.data.labels = months;
            charts.rate.data.datasets = datasets;
            charts.rate.update();
        }
    }
}

function updateAnalysis() {
    const content = document.getElementById('analysis-content');
    const summary = currentData.summary;

    // Find best strategies
    const bestEquity = summary.reduce((prev, current) =>
        prev['Equity Built (%)'] > current['Equity Built (%)'] ? prev : current
    );

    const bestPayments = summary.reduce((prev, current) =>
        prev['Total Payments'] < current['Total Payments'] ? prev : current
    );

    const bestInterest = summary.reduce((prev, current) =>
        prev['Total Interest'] < current['Total Interest'] ? prev : current
    );

    const html = `
        <div class="analysis-grid">
            <div class="analysis-item">
                <h4>🏆 Best Equity Builder</h4>
                <p><strong>${bestEquity['Strategy']}</strong></p>
                <p>${bestEquity['Equity Built (%)'].toFixed(2)}% equity built</p>
            </div>

            <div class="analysis-item">
                <h4>💰 Lowest Total Cost</h4>
                <p><strong>${bestPayments['Strategy']}</strong></p>
                <p>$${Math.round(bestPayments['Total Payments']).toLocaleString()} total payments</p>
            </div>

            <div class="analysis-item">
                <h4>📉 Lowest Interest</h4>
                <p><strong>${bestInterest['Strategy']}</strong></p>
                <p>$${Math.round(bestInterest['Total Interest']).toLocaleString()} total interest</p>
            </div>

            <div class="analysis-item">
                <h4>📊 Scenario Details</h4>
                <p><strong>${currentData.scenario.charAt(0).toUpperCase() + currentData.scenario.slice(1)}</strong> rate cut scenario</p>
                <p>25-year amortization, 3-year analysis</p>
            </div>
        </div>

        <style>
        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .analysis-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }

        .analysis-item h4 {
            margin-bottom: 10px;
            color: #333;
        }

        .analysis-item p {
            margin: 5px 0;
        }
        </style>
    `;

    content.innerHTML = html;
}

// Interactive chart functions
function resetZoom(chartName) {
    if (charts[chartName]) {
        charts[chartName].resetZoom();
    }
}

function toggleFixedRate() {
    updateCharts();
}

function updatePaymentChart() {
    if (!currentData) return;

    const paymentType = document.getElementById('paymentType').value;
    const summary = currentData.summary;

    let data, label;
    switch (paymentType) {
        case 'total':
            data = summary.map(row => row['Total Payments']);
            label = 'Total Payments';
            break;
        case 'interest':
            data = summary.map(row => row['Total Interest']);
            label = 'Total Interest';
            break;
        case 'principal':
            data = summary.map(row => row['Total Principal Paid']);
            label = 'Principal Paid';
            break;
    }

    charts.payment.data.datasets[0].data = data;
    charts.payment.data.datasets[0].label = label;
    charts.payment.options.plugins.title.text = `${label} by Strategy`;
    charts.payment.update();
}

function updateBalanceChart() {
    if (!currentData) return;

    const balanceStrategy = document.getElementById('balanceStrategy').value;
    const details = currentData.details;

    if (!details || details.length === 0) return;

    let filteredData = details;
    switch (balanceStrategy) {
        case 'variable':
            filteredData = details.filter(row =>
                row.Strategy.includes('Variable')
            );
            break;
        case 'comparison':
            // Find best and worst equity builders
            const summary = currentData.summary;
            const best = summary.reduce((prev, current) =>
                prev['Equity Built (%)'] > current['Equity Built (%)'] ? prev : current
            );
            const worst = summary.reduce((prev, current) =>
                prev['Equity Built (%)'] < current['Equity Built (%)'] ? prev : current
            );
            filteredData = details.filter(row =>
                row.Strategy === best['Strategy'] || row.Strategy === worst['Strategy']
            );
            break;
    }

    updateBalanceChartData(filteredData);
}

function updateBalanceChartData(data) {
    const strategies = [...new Set(data.map(row => row.Strategy))];
    const datasets = [];
    const colors = ['#007bff', '#28a745', '#ffc107', '#dc3545'];

    strategies.forEach((strategy, index) => {
        const strategyData = data.filter(row => row.Strategy === strategy);
        datasets.push({
            label: strategy,
            data: strategyData.map(row => row.Balance),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '20',
            fill: false,
            tension: 0.1
        });
    });

    const months = data
        .filter(row => row.Strategy === strategies[0])
        .map(row => row.Month);

    charts.balance.data.labels = months;
    charts.balance.data.datasets = datasets;
    charts.balance.update();
}

function updateEquityChart() {
    if (!currentData) return;

    const equityView = document.getElementById('equityView').value;
    const summary = currentData.summary;

    let data, label;
    switch (equityView) {
        case 'percentage':
            data = summary.map(row => row['Equity Built (%)']);
            label = 'Equity Built (%)';
            break;
        case 'dollar':
            data = summary.map(row => row['Equity Built ($)']);
            label = 'Equity Built ($)';
            break;
        case 'comparison':
            const fixedEquity = summary.find(row => row['Strategy'] === 'Full Fixed')['Equity Built (%)'];
            data = summary.map(row => row['Equity Built (%)'] - fixedEquity);
            label = 'Equity vs Fixed (%)';
            break;
    }

    if (equityView === 'comparison') {
        // Use bar chart for comparison
        charts.equity.destroy();
        const equityCtx = document.getElementById('equityChart').getContext('2d');
        charts.equity = new Chart(equityCtx, {
            type: 'bar',
            data: {
                labels: summary.map(row => row['Strategy']),
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: data.map(val => val >= 0 ? '#28a745' : '#dc3545'),
                    borderColor: data.map(val => val >= 0 ? '#1e7e34' : '#bd2130'),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Difference (%)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Equity vs Fixed Rate Strategy'
                    }
                }
            }
        });
    } else {
        // Ensure we have a doughnut chart
        if (charts.equity.config.type !== 'doughnut') {
            charts.equity.destroy();
            const equityCtx = document.getElementById('equityChart').getContext('2d');
            charts.equity = new Chart(equityCtx, {
                type: 'doughnut',
                data: {
                    labels: summary.map(row => row['Strategy']),
                    datasets: [{
                        data: data,
                        backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: label
                        }
                    }
                }
            });
        } else {
            charts.equity.data.datasets[0].data = data;
            charts.equity.options.plugins.title.text = label;
            charts.equity.update();
        }
    }
}

// Custom Form Functions
function toggleCustomForm() {
    const form = document.getElementById('custom-form');
    const isVisible = form.style.display !== 'none';

    if (isVisible) {
        form.style.display = 'none';
        document.body.style.overflow = 'auto';
    } else {
        form.style.display = 'block';
        document.body.style.overflow = 'hidden';
        updateCalculatedFields();
    }
}

function updateCalculatedFields() {
    const purchasePrice = parseFloat(document.getElementById('purchase-price').value) || 0;
    const downPaymentPercent = parseFloat(document.getElementById('down-payment-percent').value) || 0;

    const downPaymentAmount = purchasePrice * (downPaymentPercent / 100);
    const mortgageAmount = purchasePrice - downPaymentAmount;

    document.getElementById('down-payment-amount').value = Math.round(downPaymentAmount);
    document.getElementById('mortgage-amount').value = Math.round(mortgageAmount);
}

function setupFormListeners() {
    // Auto-calculate fields
    document.getElementById('purchase-price').addEventListener('input', updateCalculatedFields);
    document.getElementById('down-payment-percent').addEventListener('input', updateCalculatedFields);

    // Update analysis period max when amortization changes
    document.getElementById('amortization').addEventListener('change', function() {
        const amortizationYears = parseInt(this.value);
        const analysisPeriodField = document.getElementById('analysis-period');
        analysisPeriodField.max = amortizationYears;

        // If current analysis period exceeds new max, reset it to max
        if (parseInt(analysisPeriodField.value) > amortizationYears) {
            analysisPeriodField.value = amortizationYears;
        }

        // Update the help text
        const helpText = analysisPeriodField.nextElementSibling;
        helpText.textContent = `Enter 1-${amortizationYears} years (up to full amortization)`;
    });

    // Rate cut options toggle
    document.getElementById('enable-rate-cuts').addEventListener('change', function() {
        const rateCutOptions = document.querySelectorAll('.rate-cut-options');
        rateCutOptions.forEach(option => {
            option.style.opacity = this.checked ? '1' : '0.5';
            const inputs = option.querySelectorAll('input');
            inputs.forEach(input => input.disabled = !this.checked);
        });
    });

    // Prepayment options toggle
    document.getElementById('enable-prepayments').addEventListener('change', function() {
        const prepaymentOptions = document.querySelectorAll('.prepayment-options');
        prepaymentOptions.forEach(option => {
            option.style.opacity = this.checked ? '1' : '0.5';
            const inputs = option.querySelectorAll('input, select');
            inputs.forEach(input => input.disabled = !this.checked);
        });

        if (this.checked) {
            updatePrepaymentFields();
        }
    });

    // Prepayment type change
    document.getElementById('prepayment-type').addEventListener('change', updatePrepaymentFields);
}

function updatePrepaymentFields() {
    const prepaymentType = document.getElementById('prepayment-type').value;
    const onetimeTiming = document.getElementById('onetime-timing');
    const annualTiming = document.getElementById('annual-timing');

    // Hide all timing fields first
    onetimeTiming.style.display = 'none';
    annualTiming.style.display = 'none';

    // Show relevant timing field
    if (prepaymentType === 'onetime') {
        onetimeTiming.style.display = 'block';
    } else if (prepaymentType === 'annual') {
        annualTiming.style.display = 'block';
    }
}

function resetForm() {
    document.getElementById('mortgage-form').reset();

    // Reset to default values (matching base.env configuration)
    document.getElementById('purchase-price').value = '840000';  // Calculated from $672K loan / 80%
    document.getElementById('down-payment-percent').value = '20';
    document.getElementById('fixed-rate').value = '3.99';  // From base.env FIXED_INITIAL_RATE
    document.getElementById('fixed-term').value = '3';     // From base.env FIXED_TERM_YEARS
    document.getElementById('fixed-renewal-rate').value = '3.20';  // From base.env FIXED_RENEWAL_RATE
    document.getElementById('prime-rate').value = '4.95';  // From base.env PRIME_RATE
    document.getElementById('variable-discount').value = '0.85';  // From base.env VARIABLE_DISCOUNT_INITIAL
    document.getElementById('variable-term').value = '5';  // From base.env VARIABLE_TERM_YEARS
    document.getElementById('renewal-discount').value = '0.50';  // From base.env VARIABLE_RENEWAL_DISCOUNT
    document.getElementById('rate-cut-amount').value = '0.25';  // Standard rate cut amount
    document.getElementById('cut-schedule').value = '6,12,18,24';  // Aggressive scenario schedule
    document.getElementById('split-ratio').value = '50';  // From base.env SPLIT_RATIO
    document.getElementById('enable-rate-cuts').checked = true;
    document.getElementById('fixed-payment').checked = true;  // From base.env VARIABLE_FIXED_PAYMENT

    // Reset new fields
    document.getElementById('payment-frequency').value = 'monthly';
    document.getElementById('annual-appreciation').value = '5.0';
    document.getElementById('enable-prepayments').checked = false;
    document.getElementById('prepayment-type').value = 'none';
    document.getElementById('prepayment-amount').value = '5000';
    document.getElementById('prepayment-month').value = '12';
    document.getElementById('prepayment-start-month').value = '12';

    updateCalculatedFields();
    updatePrepaymentFields();
}

function validateForm() {
    const requiredFields = [
        'purchase-price', 'down-payment-percent', 'fixed-rate',
        'prime-rate', 'variable-discount'
    ];

    let isValid = true;
    let errors = [];

    requiredFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        const value = parseFloat(field.value);

        if (isNaN(value) || value <= 0) {
            isValid = false;
            errors.push(`${field.previousElementSibling.textContent} is required and must be positive`);
            field.style.borderColor = '#dc3545';
        } else {
            field.style.borderColor = '#dee2e6';
        }
    });

    // Validate down payment percentage
    const downPaymentPercent = parseFloat(document.getElementById('down-payment-percent').value);
    if (downPaymentPercent < 5 || downPaymentPercent > 50) {
        isValid = false;
        errors.push('Down payment must be between 5% and 50%');
        document.getElementById('down-payment-percent').style.borderColor = '#dc3545';
    }

    // Validate analysis period
    const analysisPeriod = parseInt(document.getElementById('analysis-period').value);
    const amortizationYears = parseInt(document.getElementById('amortization').value);
    if (isNaN(analysisPeriod) || analysisPeriod < 1 || analysisPeriod > amortizationYears) {
        isValid = false;
        errors.push(`Analysis period must be between 1 and ${amortizationYears} years (amortization period)`);
        document.getElementById('analysis-period').style.borderColor = '#dc3545';
    } else {
        document.getElementById('analysis-period').style.borderColor = '#dee2e6';
    }

    // Validate rate cut schedule if enabled
    if (document.getElementById('enable-rate-cuts').checked) {
        const cutSchedule = document.getElementById('cut-schedule').value;
        if (cutSchedule && !isValidCutSchedule(cutSchedule)) {
            isValid = false;
            errors.push('Cut schedule must be comma-separated numbers (e.g., 6,12,18,24)');
            document.getElementById('cut-schedule').style.borderColor = '#dc3545';
        }
    }

    if (!isValid) {
        showStatus(`Validation errors: ${errors.join('; ')}`, 'error');
    }

    return isValid;
}

function isValidCutSchedule(schedule) {
    try {
        const months = schedule.split(',').map(s => parseInt(s.trim()));
        return months.every(month => !isNaN(month) && month > 0 && month <= 60);
    } catch {
        return false;
    }
}

function gatherFormData() {
    const enableRateCuts = document.getElementById('enable-rate-cuts').checked;
    const enablePrepayments = document.getElementById('enable-prepayments').checked;

    return {
        purchase_price: parseFloat(document.getElementById('purchase-price').value),
        down_payment_percent: parseFloat(document.getElementById('down-payment-percent').value),
        amortization_years: parseInt(document.getElementById('amortization').value),
        analysis_period: parseInt(document.getElementById('analysis-period').value),
        fixed_rate: parseFloat(document.getElementById('fixed-rate').value) / 100,
        fixed_term: parseInt(document.getElementById('fixed-term').value),
        fixed_renewal_rate: parseFloat(document.getElementById('fixed-renewal-rate').value) / 100,
        prime_rate: parseFloat(document.getElementById('prime-rate').value) / 100,
        variable_discount: parseFloat(document.getElementById('variable-discount').value) / 100,
        variable_term: parseInt(document.getElementById('variable-term').value),
        renewal_discount: parseFloat(document.getElementById('renewal-discount').value) / 100,
        enable_rate_cuts: enableRateCuts,
        rate_cut_amount: enableRateCuts ? parseFloat(document.getElementById('rate-cut-amount').value) / 100 : 0,
        cut_schedule: enableRateCuts ? document.getElementById('cut-schedule').value : '',
        split_ratio: parseFloat(document.getElementById('split-ratio').value) / 100,
        fixed_payment: document.getElementById('fixed-payment').checked,

        // New payment and prepayment options
        payment_frequency: document.getElementById('payment-frequency').value,
        annual_appreciation: parseFloat(document.getElementById('annual-appreciation').value) / 100,
        enable_prepayments: enablePrepayments,
        prepayment_type: enablePrepayments ? document.getElementById('prepayment-type').value : 'none',
        prepayment_amount: enablePrepayments ? parseFloat(document.getElementById('prepayment-amount').value) : 0,
        prepayment_month: enablePrepayments ? parseInt(document.getElementById('prepayment-month').value) : 12,
        prepayment_start_month: enablePrepayments ? parseInt(document.getElementById('prepayment-start-month').value) : 12
    };
}

async function runCustomAnalysis() {
    if (!validateForm()) {
        return;
    }

    const formData = gatherFormData();

    showStatus('Running custom analysis...', 'loading');

    try {
        const response = await fetch('/run_custom_scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            const result = await response.json();

            // Close the form
            toggleCustomForm();

            // Load the custom results
            currentData = {
                scenario: 'custom',
                summary: result.summary,
                details: result.details,
                homeValueData: result.homeValueData
            };

            updateDashboard();
            showStatus('Custom analysis completed successfully!', 'success');
            setTimeout(hideStatus, 3000);

        } else {
            const error = await response.json();
            showStatus(`Error: ${error.message || 'Failed to run custom analysis'}`, 'error');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

function updateScheduleTable() {
    if (!currentData) return;

    const selectedStrategy = document.getElementById('scheduleStrategy').value;
    const content = document.getElementById('schedule-content');

    if (!selectedStrategy) {
        content.innerHTML = '<div class="loading">Select a strategy to view the full amortization schedule</div>';
        return;
    }

    const details = currentData.details;
    if (!details || details.length === 0) {
        content.innerHTML = '<div class="error">No schedule data available</div>';
        return;
    }

    // Filter data for selected strategy
    const strategyData = details.filter(row => row.Strategy === selectedStrategy);

    if (strategyData.length === 0) {
        content.innerHTML = '<div class="error">No data found for selected strategy</div>';
        return;
    }

    // Create table
    let html = `
        <div class="schedule-container">
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Month</th>
                        <th>Payment</th>
                        <th>Principal</th>
                        <th>Interest</th>
                        <th>Balance</th>
                        <th>Rate (%)</th>
                    </tr>
                </thead>
                <tbody>
    `;

    strategyData.forEach(row => {
        html += `
            <tr>
                <td>${row.Month}</td>
                <td>$${Math.round(row.Payment).toLocaleString()}</td>
                <td>$${Math.round(row['Principal Paid']).toLocaleString()}</td>
                <td>$${Math.round(row['Interest Paid']).toLocaleString()}</td>
                <td>$${Math.round(row.Balance).toLocaleString()}</td>
                <td>${row.Rate.toFixed(2)}%</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
        <div style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 5px; font-size: 12px; color: #666;">
            Showing ${strategyData.length} months of amortization schedule for ${selectedStrategy}
        </div>
    `;

    content.innerHTML = html;
}


function updateHomeValueChart() {
    if (!currentData) {
        return;
    }

    if (!currentData.homeValueData) {
        return;
    }

    const homeValueView = document.getElementById('homeValueView').value;
    const homeValueData = currentData.homeValueData;
    const summary = currentData.summary;

    switch (homeValueView) {
        case 'netcash':
            updateHomeValueChartNetCash(homeValueData);
            break;
        case 'totalreturn':
            updateHomeValueChartTotalReturn(homeValueData);
            break;
        case 'homevalue':
            updateHomeValueChartGrowth(homeValueData);
            break;
        case 'comparison':
            updateHomeValueChartComparison(homeValueData, summary);
            break;
    }
}

function updateHomeValueChartNetCash(homeValueData) {
    const strategies = Object.keys(homeValueData);
    const netCashData = strategies.map(strategy => homeValueData[strategy].netCashOnSale);

    charts.homeValue.data.labels = strategies;
    charts.homeValue.data.datasets[0].data = netCashData;
    charts.homeValue.data.datasets[0].label = 'Net Cash on Sale';
    charts.homeValue.options.plugins.title.text = 'Net Cash on Sale by Strategy';
    charts.homeValue.update();
}

function updateHomeValueChartTotalReturn(homeValueData) {
    const strategies = Object.keys(homeValueData);
    const totalReturnData = strategies.map(strategy => homeValueData[strategy].totalReturn);

    charts.homeValue.data.labels = strategies;
    charts.homeValue.data.datasets[0].data = totalReturnData;
    charts.homeValue.data.datasets[0].label = 'Total Return on Investment';
    charts.homeValue.options.plugins.title.text = 'Total Return on Investment by Strategy';
    charts.homeValue.update();
}

function updateHomeValueChartGrowth(homeValueData) {
    const strategies = Object.keys(homeValueData);
    const homeValueGrowth = strategies.map(strategy => homeValueData[strategy].homeValue);

    charts.homeValue.data.labels = strategies;
    charts.homeValue.data.datasets[0].data = homeValueGrowth;
    charts.homeValue.data.datasets[0].label = 'Home Value';
    charts.homeValue.options.plugins.title.text = 'Home Value Growth';
    charts.homeValue.update();
}

function updateHomeValueChartComparison(homeValueData, summary) {
    // Find best and worst equity builders for comparison
    const best = summary.reduce((prev, current) =>
        prev['Equity Built (%)'] > current['Equity Built (%)'] ? prev : current
    );
    const worst = summary.reduce((prev, current) =>
        prev['Equity Built (%)'] < current['Equity Built (%)'] ? prev : current
    );

    const strategies = [best['Strategy'], worst['Strategy']];
    const netCashData = strategies.map(strategy => homeValueData[strategy]?.netCashOnSale || 0);

    charts.homeValue.data.labels = strategies;
    charts.homeValue.data.datasets[0].data = netCashData;
    charts.homeValue.data.datasets[0].label = 'Net Cash on Sale';
    charts.homeValue.options.plugins.title.text = 'Best vs Worst Strategy - Net Cash on Sale';
    charts.homeValue.update();
}

function loadConservativePreset() {
    resetForm();
    // Conservative: 2 rate cuts at months 6 & 12
    document.getElementById('cut-schedule').value = '6,12';
    document.getElementById('analysis-period').value = '3';
    document.getElementById('purchase-price').value = '840000';
    updateCalculatedFields();
}

function loadAggressivePreset() {
    resetForm();
    // Aggressive: 4 rate cuts at months 6, 12, 18, 24
    document.getElementById('cut-schedule').value = '6,12,18,24';
    document.getElementById('analysis-period').value = '3';
    document.getElementById('purchase-price').value = '840000';
    updateCalculatedFields();
}

function loadHighLoanPreset() {
    resetForm();
    // High Loan: Same as aggressive but $1M loan over 5 years
    document.getElementById('cut-schedule').value = '6,12,18,24';
    document.getElementById('analysis-period').value = '5';
    document.getElementById('purchase-price').value = '1250000';  // $1M loan / 80%
    updateCalculatedFields();
}

// Initialize form listeners when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupFormListeners();

    // Auto-open the custom form so users can see default values
    setTimeout(() => {
        console.log('Auto-opening form...');
        try {
            toggleCustomForm();
            // Load aggressive preset by default (matches the default cut schedule)
            loadAggressivePreset();
            console.log('Form opened and preset loaded');
        } catch (error) {
            console.error('Error auto-opening form:', error);
        }
    }, 1000); // Increased delay to ensure page is fully loaded
});