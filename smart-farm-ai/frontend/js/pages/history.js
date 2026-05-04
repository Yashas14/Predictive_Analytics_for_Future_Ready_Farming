// Prediction history page

const HistoryPage = {
    async render() {
        const container = document.getElementById('page-container');
        container.innerHTML = `
            <div class="page-header">
                <h1>📈 Prediction History</h1>
                <p>View, filter, and export all historical predictions made by the system.</p>
                <div class="chips">
                    ${Components.chip('Filter & Search')}
                    ${Components.chip('CSV Export')}
                    ${Components.chip('Trend Analysis')}
                </div>
            </div>

            ${Components.sectionHeader('🔍', 'Filters', 'Refine your search')}
            <div class="glass-panel" style="margin-bottom: 24px;">
                <div class="grid-4">
                    <div class="form-group">
                        <label class="form-label">Show Last</label>
                        <select class="form-input form-select" id="hist-limit">
                            <option value="20">20 records</option>
                            <option value="50" selected>50 records</option>
                            <option value="100">100 records</option>
                            <option value="200">200 records</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <select class="form-input form-select" id="hist-category">
                            <option value="all">All</option>
                            <option value="high">High Yield</option>
                            <option value="medium">Medium Yield</option>
                            <option value="low">Low Yield</option>
                        </select>
                    </div>
                    <div class="form-group" style="display: flex; align-items: flex-end;">
                        <button class="btn btn-primary btn-full" onclick="HistoryPage.loadData()">
                            🔍 SEARCH
                        </button>
                    </div>
                    <div class="form-group" style="display: flex; align-items: flex-end;">
                        <button class="btn btn-secondary btn-full" onclick="HistoryPage.exportCSV()">
                            📥 EXPORT
                        </button>
                    </div>
                </div>
            </div>

            <div id="history-content">${Components.loading('Loading history...')}</div>
        `;

        this.loadData();
    },

    async loadData() {
        const limit = parseInt(document.getElementById('hist-limit').value) || 50;
        const category = document.getElementById('hist-category').value;
        const content = document.getElementById('history-content');
        content.innerHTML = Components.loading('Fetching predictions...');

        try {
            const data = await Api.getHistory(limit);
            let predictions = data?.predictions || [];

            // Filter by category
            if (category !== 'all') {
                predictions = predictions.filter(p => p.yield_category === category);
            }

            this.predictions = predictions;
            this.renderData(predictions);
        } catch (error) {
            content.innerHTML = Components.emptyState('⚠️', `Error: ${error.message}`);
        }
    },

    renderData(predictions) {
        const content = document.getElementById('history-content');

        if (!predictions.length) {
            content.innerHTML = Components.emptyState('📭', 'No predictions found. Try adjusting filters or make some predictions first.');
            return;
        }

        const yields = predictions.map(p => p.predicted_yield).filter(Boolean);
        const avgYield = yields.length ? (yields.reduce((a, b) => a + b, 0) / yields.length) : 0;
        const highPct = predictions.length ? 
            ((predictions.filter(p => p.yield_category === 'high').length / predictions.length) * 100).toFixed(1) : 0;

        content.innerHTML = `
            <!-- Summary Cards -->
            <div class="grid-4">
                ${Components.metricCard('Total Records', Components.formatNumber(predictions.length), '', '📝')}
                ${Components.metricCard('Avg Yield', Components.formatNumber(avgYield), 'kg/ha', '🌾')}
                ${Components.metricCard('High Yield %', `${highPct}%`, '', '📈')}
                ${Components.metricCard('Records Shown', `${predictions.length}`, '', '📋')}
            </div>

            <div class="spacer-md"></div>

            <!-- Trend Chart -->
            ${Components.sectionHeader('📈', 'Prediction Trend', 'Yield over time')}
            <div class="chart-container" style="margin-bottom: 24px;">
                <canvas id="history-trend-chart" height="200"></canvas>
            </div>

            <!-- Data Table -->
            ${Components.sectionHeader('📋', 'Prediction Records')}
            <div class="glass-panel" style="overflow-x: auto; max-height: 500px; overflow-y: auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Timestamp</th>
                            <th>Yield (kg/ha)</th>
                            <th>CI Lower</th>
                            <th>CI Upper</th>
                            <th>Category</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${predictions.map((p, i) => `
                            <tr>
                                <td style="color: var(--text-muted);">${i + 1}</td>
                                <td style="font-size: 11px; font-family: JetBrains Mono;">${this.formatTimestamp(p.timestamp)}</td>
                                <td style="font-family: JetBrains Mono; color: var(--accent-green); font-weight: 600;">
                                    ${Components.formatNumber(p.predicted_yield)}
                                </td>
                                <td style="font-family: JetBrains Mono;">${Components.formatNumber(p.confidence_interval_lower || p.confidence_lower)}</td>
                                <td style="font-family: JetBrains Mono;">${Components.formatNumber(p.confidence_interval_upper || p.confidence_upper)}</td>
                                <td>${Components.yieldBadge(p.yield_category)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // Render trend chart
        this.renderTrendChart(predictions);
    },

    renderTrendChart(predictions) {
        const yields = predictions.map(p => p.predicted_yield || 0);
        const labels = predictions.map((_, i) => `#${i + 1}`);
        const categories = predictions.map(p => p.yield_category || 'medium');
        const colors = categories.map(c => c === 'high' ? '#00E676' : c === 'low' ? '#FF5252' : '#FFD600');

        Components.createChart('history-trend-chart', {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Predicted Yield',
                    data: yields,
                    borderColor: '#BAFF29',
                    backgroundColor: 'rgba(186, 255, 41, 0.04)',
                    borderWidth: 2,
                    pointBackgroundColor: colors,
                    pointBorderColor: '#060D1A',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(26, 51, 80, 0.3)' } },
                    y: { grid: { color: 'rgba(26, 51, 80, 0.3)' }, title: { display: true, text: 'Yield (kg/ha)' } }
                }
            }
        });
    },

    formatTimestamp(ts) {
        if (!ts) return '—';
        try {
            const d = new Date(ts);
            return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
        } catch { return ts; }
    },

    exportCSV() {
        const predictions = this.predictions || [];
        if (!predictions.length) {
            Components.showToast('No data to export', 'warning');
            return;
        }

        let csv = 'Row,Timestamp,Predicted_Yield,CI_Lower,CI_Upper,Category\n';
        predictions.forEach((p, i) => {
            csv += `${i + 1},"${p.timestamp || ''}",${p.predicted_yield},${p.confidence_interval_lower || p.confidence_lower || ''},${p.confidence_interval_upper || p.confidence_upper || ''},${p.yield_category}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `prediction_history_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
        Components.showToast('CSV exported successfully!', 'success');
    }
};

window.HistoryPage = HistoryPage;
