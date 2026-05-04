// Yield predictor page

const PredictorPage = {
    lastResult: null,

    render() {
        const container = document.getElementById('page-container');
        container.innerHTML = `
            <div class="page-header">
                <h1>🔬 Yield Predictor</h1>
                <p>Enter farm parameters to get an AI-powered yield prediction with explainability analysis.</p>
                <div class="chips">
                    ${Components.chip('12 Features')}
                    ${Components.chip('Ensemble Model')}
                    ${Components.chip('95% CI')}
                    ${Components.chip('SHAP Analysis')}
                </div>
            </div>

            <div class="form-panel">
                <!-- Weather Section -->
                ${Components.sectionHeader('🌡️', 'Weather Conditions', 'Real-time atmospheric data')}
                <div class="grid-3">
                    <div class="form-group">
                        <label class="form-label">Temperature (°C)</label>
                        <input type="number" class="form-input" id="p-temp" value="25" step="0.5" min="-50" max="60">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Dew Point Temperature (°C)</label>
                        <input type="number" class="form-input" id="p-dew" value="12" step="0.5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Wind Direction (°)</label>
                        <input type="number" class="form-input" id="p-wind-dir" value="180" min="0" max="360" step="5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Wind Speed (km/h)</label>
                        <input type="number" class="form-input" id="p-wind-speed" value="15" min="0" step="1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Precipitation (mm)</label>
                        <input type="number" class="form-input" id="p-precip" value="5" min="0" step="0.5">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Sea Level Pressure (hPa)</label>
                        <input type="number" class="form-input" id="p-pressure" value="1013.25" step="0.5">
                    </div>
                </div>

                <div class="spacer-md"></div>

                <!-- Farm Section -->
                ${Components.sectionHeader('🏭', 'Farm Profile', 'Farm infrastructure data')}
                <div class="grid-3">
                    <div class="form-group">
                        <label class="form-label">Farm Area (acres)</label>
                        <input type="number" class="form-input" id="p-area" value="150" min="0.1" step="10">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Ingredient Type (0-10)</label>
                        <input type="number" class="form-input" id="p-ingredient" value="3" min="0" max="10">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Farming Company Code</label>
                        <input type="number" class="form-input" id="p-company" value="12" min="0" max="50">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Location Code</label>
                        <input type="number" class="form-input" id="p-location" value="45" min="0" max="100">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Processing Plants</label>
                        <input type="number" class="form-input" id="p-plants" value="5" min="1">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Unix Timestamp</label>
                        <input type="number" class="form-input" id="p-unix" value="${Math.floor(Date.now() / 1000)}">
                    </div>
                </div>

                <div class="spacer-md"></div>

                <button class="btn btn-primary btn-full btn-lg" onclick="PredictorPage.predict()">
                    🚀 PREDICT YIELD
                </button>
            </div>

            <!-- Results Area -->
            <div id="prediction-results"></div>
        `;
    },

    async predict() {
        const data = {
            farm_area: parseFloat(document.getElementById('p-area').value),
            temp_obs: parseFloat(document.getElementById('p-temp').value),
            wind_direction: parseFloat(document.getElementById('p-wind-dir').value),
            dew_temp: parseFloat(document.getElementById('p-dew').value),
            pressure_sea_level: parseFloat(document.getElementById('p-pressure').value),
            precipitation: parseFloat(document.getElementById('p-precip').value),
            wind_speed: parseFloat(document.getElementById('p-wind-speed').value),
            unix_sec: parseInt(document.getElementById('p-unix').value),
            ingredient_type: parseInt(document.getElementById('p-ingredient').value),
            farming_company: parseInt(document.getElementById('p-company').value),
            deidentified_location: parseInt(document.getElementById('p-location').value),
            num_processing_plants: parseInt(document.getElementById('p-plants').value),
        };

        const resultsDiv = document.getElementById('prediction-results');
        resultsDiv.innerHTML = `<div class="spacer-md"></div>${Components.loading('🧠 Analyzing farm data...')}`;

        try {
            const result = await Api.predictSingle(data);
            this.lastResult = result;
            this.renderResults(result);
            Components.showToast('Prediction complete!', 'success');
        } catch (error) {
            resultsDiv.innerHTML = '';
            Components.showToast(`Error: ${error.message}`, 'error');
        }
    },

    renderResults(result) {
        const resultsDiv = document.getElementById('prediction-results');
        const ciWidth = result.confidence_interval_upper - result.confidence_interval_lower;
        const ciPct = result.predicted_yield ? ((ciWidth / result.predicted_yield) * 100).toFixed(1) : 0;
        
        // SHAP chart
        const shapValues = result.shap_values || {};
        const shapEntries = Object.entries(shapValues).slice(0, 10);
        
        // Recommendations
        const recs = (result.recommendation || '').split(' | ').filter(Boolean);
        const recIcons = ['🌱', '💧', '🌡️', '📋', '⚡'];

        resultsDiv.innerHTML = `
            <div class="spacer-md"></div>

            <!-- Main Result -->
            <div class="prediction-result">
                <div class="result-label">Predicted Yield</div>
                <div class="result-value">${Components.formatNumber(result.predicted_yield)}</div>
                <div class="result-unit">kg/hectare</div>
                <div class="result-ci">
                    <span class="ci-badge">
                        95% CI: ${Components.formatNumber(result.confidence_interval_lower)} — ${Components.formatNumber(result.confidence_interval_upper)} kg/ha
                    </span>
                </div>
                <div class="result-badge">
                    ${Components.yieldBadge(result.yield_category)}
                </div>
            </div>

            <!-- Stats Row -->
            <div class="grid-4">
                ${Components.metricCard('Predicted Yield', `${Components.formatNumber(result.predicted_yield)}`, 'kg/hectare', '🎯')}
                ${Components.metricCard('CI Width', `±${Components.formatNumber(ciWidth / 2)}`, `${ciPct}% range`, '📊')}
                ${Components.metricCard('Lower Bound', `${Components.formatNumber(result.confidence_interval_lower)}`, 'kg/ha', '📉')}
                ${Components.metricCard('Upper Bound', `${Components.formatNumber(result.confidence_interval_upper)}`, 'kg/ha', '📈')}
            </div>

            <div class="spacer-md"></div>

            <!-- SHAP + Recommendations -->
            <div class="grid-1-1">
                <div>
                    ${Components.sectionHeader('🔍', 'SHAP Feature Impact', 'Explainability analysis')}
                    <div class="chart-container">
                        ${shapEntries.length ? '<canvas id="shap-chart" height="300"></canvas>' : 
                            Components.emptyState('🔍', 'SHAP values not available.')}
                    </div>
                </div>
                <div>
                    ${Components.sectionHeader('💡', 'Smart Recommendations', 'AI-generated insights')}
                    <div>
                        ${recs.length ? recs.map((rec, i) => `
                            <div class="rec-card">
                                <span style="font-size:16px;">${recIcons[i % recIcons.length]}</span>
                                <span>${rec}</span>
                            </div>
                        `).join('') : Components.emptyState('💡', 'No recommendations available.')}
                    </div>
                </div>
            </div>
        `;

        // Render SHAP chart
        if (shapEntries.length) {
            this.renderShapChart(shapEntries);
        }
    },

    renderShapChart(entries) {
        const labels = entries.map(([k]) => k);
        const values = entries.map(([, v]) => v);
        const colors = values.map(v => v > 0 ? 'rgba(186, 255, 41, 0.8)' : 'rgba(255, 82, 82, 0.8)');

        Components.createChart('shap-chart', {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 4,
                    barThickness: 18,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { 
                        grid: { color: 'rgba(26, 51, 80, 0.3)' },
                        title: { display: true, text: 'SHAP Value' }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    },
};

window.PredictorPage = PredictorPage;
