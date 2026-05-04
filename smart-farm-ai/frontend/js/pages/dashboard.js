// Dashboard page

const DashboardPage = {
    async render() {
        const container = document.getElementById('page-container');
        container.innerHTML = Components.loading('Loading dashboard...');

        // Fetch data in parallel
        let health = null, metrics = null, history = null;
        try {
            [health, metrics, history] = await Promise.allSettled([
                Api.getHealth(),
                Api.getModelMetrics(),
                Api.getHistory(20),
            ]).then(results => results.map(r => r.status === 'fulfilled' ? r.value : null));
        } catch (e) { /* continue with nulls */ }

        const totalPredictions = history?.total || 0;
        const predictions = history?.predictions || [];
        const yields = predictions.map(p => p.predicted_yield).filter(Boolean);
        const avgYield = yields.length ? (yields.reduce((a, b) => a + b, 0) / yields.length) : 0;
        const modelR2 = metrics?.r2_score || 0;
        const isOnline = health?.model_loaded || false;

        container.innerHTML = `
            <!-- Hero Banner -->
            <div class="hero-banner">
                <div class="hero-content">
                    <div class="hero-icon">🌾</div>
                    <h1 class="hero-title">AgriSense AI</h1>
                    <p class="hero-subtitle">Next-Generation Yield Intelligence Platform</p>
                    <div class="hero-pills">
                        ${Components.statPill('RF + XGBoost + LightGBM')}
                        ${Components.statPill('SHAP Explainability')}
                        ${Components.statPill('Real-time Predictions')}
                    </div>
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="grid-4">
                ${Components.metricCard('Total Predictions', Components.formatNumber(totalPredictions), 'All time', '🎯')}
                ${Components.metricCard('Avg Yield', Components.formatNumber(avgYield), 'kg/hectare', '📊')}
                ${Components.metricCard('Model R²', modelR2 ? `${(modelR2 * 100).toFixed(1)}%` : 'N/A', 'Ensemble', '🏆')}
                ${Components.metricCard('Status', isOnline ? '● Online' : '○ Offline', 'v1.0.0', '⚡')}
            </div>

            <div class="spacer-md"></div>

            <!-- Charts -->
            <div class="grid-2-1">
                <div>
                    ${Components.sectionHeader('📈', 'Recent Predictions', 'Last 20 predictions')}
                    <div class="chart-container">
                        ${predictions.length ? '<canvas id="trend-chart"></canvas>' : 
                            Components.emptyState('🌱', 'No predictions yet. Use the Yield Predictor to get started!')}
                    </div>
                </div>
                <div>
                    ${Components.sectionHeader('🎯', 'Yield Distribution', 'Category breakdown')}
                    <div class="chart-container">
                        ${predictions.length ? '<canvas id="pie-chart"></canvas>' : 
                            Components.emptyState('📊', 'No data yet.')}
                    </div>
                </div>
            </div>

            <div class="spacer-md"></div>

            <!-- Quick Predict -->
            ${Components.sectionHeader('⚡', 'Quick Prediction', 'Fast yield estimation')}
            <div class="glass-panel">
                <div class="grid-4">
                    <div class="form-group">
                        <label class="form-label">Farm Area (acres)</label>
                        <input type="number" class="form-input" id="qp-farm-area" value="150" step="10">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Temperature (°C)</label>
                        <input type="number" class="form-input" id="qp-temp" value="25" step="0.5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Precipitation (mm)</label>
                        <input type="number" class="form-input" id="qp-precip" value="5" step="0.5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Wind Speed (km/h)</label>
                        <input type="number" class="form-input" id="qp-wind" value="15" step="1">
                    </div>
                </div>
                <div class="spacer-sm"></div>
                <button class="btn btn-primary btn-full" onclick="DashboardPage.quickPredict()">
                    ⚡ QUICK PREDICT
                </button>
                <div id="quick-result" class="spacer-sm"></div>
            </div>
        `;

        // Render charts
        if (predictions.length) {
            this.renderTrendChart(predictions);
            this.renderPieChart(predictions);
        }
    },

    renderTrendChart(predictions) {
        const yields = predictions.map(p => p.predicted_yield || 0);
        const categories = predictions.map(p => p.yield_category || 'medium');
        const colors = categories.map(c => 
            c === 'high' ? '#00E676' : c === 'low' ? '#FF5252' : '#FFD600'
        );

        Components.createChart('trend-chart', {
            type: 'line',
            data: {
                labels: yields.map((_, i) => `#${i + 1}`),
                datasets: [{
                    label: 'Predicted Yield',
                    data: yields,
                    borderColor: '#BAFF29',
                    backgroundColor: 'rgba(186, 255, 41, 0.05)',
                    borderWidth: 2.5,
                    pointBackgroundColor: colors,
                    pointBorderColor: '#060D1A',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    fill: true,
                    tension: 0.4,
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

    renderPieChart(predictions) {
        const categories = predictions.map(p => p.yield_category || 'medium');
        const high = categories.filter(c => c === 'high').length;
        const medium = categories.filter(c => c === 'medium').length;
        const low = categories.filter(c => c === 'low').length;

        Components.createChart('pie-chart', {
            type: 'doughnut',
            data: {
                labels: ['High', 'Medium', 'Low'],
                datasets: [{
                    data: [high, medium, low],
                    backgroundColor: ['#00E676', '#FFD600', '#FF5252'],
                    borderColor: '#060D1A',
                    borderWidth: 3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '65%',
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true } }
                }
            }
        });
    },

    async quickPredict() {
        const data = {
            farm_area: parseFloat(document.getElementById('qp-farm-area').value) || 150,
            temp_obs: parseFloat(document.getElementById('qp-temp').value) || 25,
            precipitation: parseFloat(document.getElementById('qp-precip').value) || 5,
            wind_speed: parseFloat(document.getElementById('qp-wind').value) || 15,
            wind_direction: 180,
            dew_temp: 12,
            pressure_sea_level: 1013.25,
            unix_sec: Math.floor(Date.now() / 1000),
            ingredient_type: 3,
            farming_company: 12,
            deidentified_location: 45,
            num_processing_plants: 5,
        };

        const resultDiv = document.getElementById('quick-result');
        resultDiv.innerHTML = Components.loading('Predicting...');

        try {
            const result = await Api.predictSingle(data);
            resultDiv.innerHTML = `
                <div class="spacer-sm"></div>
                <div class="grid-3">
                    ${Components.metricCard('Predicted Yield', `${Components.formatNumber(result.predicted_yield)} kg/ha`, '', '🌾')}
                    ${Components.metricCard('95% CI', `${Components.formatNumber(result.confidence_interval_lower)} — ${Components.formatNumber(result.confidence_interval_upper)}`, '', '📐')}
                    ${Components.metricCard('Category', result.yield_category?.toUpperCase() || 'N/A', '', '🏷️')}
                </div>
            `;
            Components.showToast('Prediction successful!', 'success');
        } catch (error) {
            resultDiv.innerHTML = '';
            Components.showToast(`Prediction failed: ${error.message}`, 'error');
        }
    }
};

window.DashboardPage = DashboardPage;
