// Policy Inequality Simulator - Frontend JavaScript

// DOM Elements
const policyInput = document.getElementById('policyInput');
const simulateBtn = document.getElementById('simulateBtn');
const clearBtn = document.getElementById('clearBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const examplesList = document.getElementById('examplesList');
const useLlmCheckbox = document.getElementById('useLlmCheckbox');

// Chart instance
let distributionChart = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExamples();
    attachEventListeners();
});

// Event Listeners
function attachEventListeners() {
    simulateBtn.addEventListener('click', runSimulation);
    clearBtn.addEventListener('click', clearForm);

    // Allow Enter to submit (with Shift+Enter for new line)
    policyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            runSimulation();
        }
    });
}

// Load Examples
async function loadExamples() {
    try {
        const response = await fetch('/api/examples');
        const data = await response.json();

        examplesList.innerHTML = '';
        data.examples.forEach(example => {
            const chip = document.createElement('span');
            chip.className = 'example-chip';
            chip.textContent = example.title;
            chip.title = example.description;
            chip.addEventListener('click', () => {
                policyInput.value = example.description;
                policyInput.focus();
            });
            examplesList.appendChild(chip);
        });
    } catch (error) {
        console.error('Failed to load examples:', error);
    }
}

// Run Simulation
async function runSimulation() {
    const policyDescription = policyInput.value.trim();

    if (!policyDescription) {
        alert('Please enter a policy description');
        return;
    }

    // Show loading state
    setLoading(true);
    hideResults();
    hideError();

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                policy_description: policyDescription,
                use_llm: useLlmCheckbox.checked
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
        } else {
            displayError(data.error || 'Simulation failed');
        }
    } catch (error) {
        displayError(`Network error: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// Display Results
function displayResults(data) {
    // Hide error, show results
    errorSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Summary
    document.getElementById('summaryText').textContent = data.summary;

    // Inequality metrics
    const ineq = data.inequality;
    document.getElementById('giniBefore').textContent = ineq.gini_before.toFixed(3);
    document.getElementById('giniAfter').textContent = ineq.gini_after.toFixed(3);
    document.getElementById('giniChange').textContent = formatChange(ineq.gini_pct_change);
    document.getElementById('giniChange').className = 'metric-change ' +
        (ineq.gini_change < 0 ? 'positive' : 'negative');

    document.getElementById('povertyBefore').textContent = ineq.poverty_rate_before.toFixed(1) + '%';
    document.getElementById('povertyAfter').textContent = ineq.poverty_rate_after.toFixed(1) + '%';
    document.getElementById('povertyChange').textContent = formatChange(ineq.poverty_change, true);
    document.getElementById('povertyChange').className = 'metric-change ' +
        (ineq.poverty_change < 0 ? 'positive' : 'negative');

    // Cost metrics
    const costs = data.costs;
    document.getElementById('totalCost').textContent = formatCurrency(costs.total_annual_cost);
    document.getElementById('beneficiaries').textContent = formatNumber(costs.n_beneficiaries);
    document.getElementById('avgBenefit').textContent = formatCurrency(costs.avg_benefit_per_beneficiary);
    document.getElementById('costPerGini').textContent = formatCurrency(costs.cost_per_gini_point);

    // Distribution table
    displayDistribution(data.distribution);

    // Chart
    displayChart(data.distribution);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display Distribution Table
function displayDistribution(distribution) {
    const tbody = document.getElementById('distributionTableBody');
    tbody.innerHTML = '';

    const quintiles = [
        { key: 'Q1', label: 'Bottom 20%' },
        { key: 'Q2', label: 'Second 20%' },
        { key: 'Q3', label: 'Middle 20%' },
        { key: 'Q4', label: 'Fourth 20%' },
        { key: 'Q5', label: 'Top 20%' }
    ];

    quintiles.forEach(q => {
        if (distribution[q.key]) {
            const d = distribution[q.key];
            const row = document.createElement('tr');

            const pctChange = d.pct_income_change;
            const pctClass = pctChange > 0 ? 'positive' : 'negative';

            row.innerHTML = `
                <td class="quintile-label">${q.label}</td>
                <td>${formatCurrency(d.avg_income_before)}</td>
                <td>${formatCurrency(d.avg_income_after)}</td>
                <td>${formatCurrency(d.avg_benefit)}</td>
                <td class="pct-change ${pctClass}">${formatChange(pctChange)}</td>
            `;

            tbody.appendChild(row);
        }
    });
}

// Display Chart
function displayChart(distribution) {
    const ctx = document.getElementById('distributionChart');

    // Destroy existing chart if it exists
    if (distributionChart) {
        distributionChart.destroy();
    }

    const quintiles = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5'];
    const labels = ['Bottom 20%', 'Second 20%', 'Middle 20%', 'Fourth 20%', 'Top 20%'];

    const incomeBefore = quintiles.map(q =>
        distribution[q] ? distribution[q].avg_income_before : 0
    );
    const incomeAfter = quintiles.map(q =>
        distribution[q] ? distribution[q].avg_income_after : 0
    );

    distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Before Policy',
                    data: incomeBefore,
                    backgroundColor: 'rgba(153, 102, 255, 0.5)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                },
                {
                    label: 'After Policy',
                    data: incomeAfter,
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Average Income by Quintile'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += formatCurrency(context.parsed.y);
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

// Display Error
function displayError(message) {
    resultsSection.style.display = 'none';
    errorSection.style.display = 'block';
    document.getElementById('errorText').textContent = message;
}

// Hide sections
function hideResults() {
    resultsSection.style.display = 'none';
}

function hideError() {
    errorSection.style.display = 'none';
}

// Clear Form
function clearForm() {
    policyInput.value = '';
    hideResults();
    hideError();
    policyInput.focus();
}

// Set Loading State
function setLoading(isLoading) {
    if (isLoading) {
        simulateBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
    } else {
        simulateBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Formatting Helpers
function formatCurrency(value) {
    if (value >= 1e12) {
        return '$' + (value / 1e12).toFixed(2) + 'T';
    } else if (value >= 1e9) {
        return '$' + (value / 1e9).toFixed(2) + 'B';
    } else if (value >= 1e6) {
        return '$' + (value / 1e6).toFixed(2) + 'M';
    } else if (value >= 1e3) {
        return '$' + (value / 1e3).toFixed(1) + 'K';
    } else {
        return '$' + value.toFixed(0);
    }
}

function formatNumber(value) {
    return value.toLocaleString('en-US', { maximumFractionDigits: 0 });
}

function formatChange(value, isPercentagePoint = false) {
    const sign = value > 0 ? '+' : '';
    const suffix = isPercentagePoint ? ' pp' : '%';
    return sign + value.toFixed(1) + suffix;
}
