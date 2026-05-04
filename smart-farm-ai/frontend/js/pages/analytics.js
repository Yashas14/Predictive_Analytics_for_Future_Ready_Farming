// Analytics page

const AnalyticsPage = {
    async render() {
        const container = document.getElementById('page-container');
        container.innerHTML = Components.loading('Loading analytics...');

        let metrics = null, featureImportance = null, comparison = null, history = null;
        try {
            [metrics, featureImportance, comparison, history] = await Promise.allSettled([
                Api.getModelMetrics(),
                Api.getFeatureImportance(),
                Api.getModelComparison(),
                Api.getHistory(100),
            ]).then(results => results.map(r => r.status === 'fulfilled' ? r.value : null));
        } catch (e) { /* continue */ }

        const predictions = history?.predictions || [];

        container.innerHTML = `
            <div class="page-header">
                <h1>📊 Analytics Dashboard</h1>
                <p>Model performance metrics, feature importance, and predictive insights.</p>
                <div class="chips">
                    ${Components.chip('Ensemble Performance')}
                    ${Components.chip('Cross-Validation')}
                    ${Components.chip('Feature Analysis')}
                </div>
            </div>

            <!-- Model Metrics -->
            ${Components.sectionHeader('🎯', 'Model Performance', 'Evaluation metrics')}
            ${metrics ? `
                <div class="grid-4">
                    ${Components.metricCard('R² Score', (metrics.r2_score || 0).toFixed(4), 'Test set', '🎯')}
                    ${Components.metricCard('RMSE', Components.formatNumber(metrics.rmse || 0, 2), 'Test set', '📏')}
                    ${Components.metricCard('MAE', Components.formatNumber(metrics.mae || 0, 2), 'Test set', '📐')}
                    ${Components.metricCard('CV R² (5-fold)', `${(metrics.cv_r2_mean || 0).toFixed(4)} ± ${(metrics.cv_r2_std || 0).toFixed(4)}`, '', '🔄')}
                </div>
            ` : Components.emptyState('📉', 'Model metrics not available.')}

            <div class="spacer-md"></div>

            <!-- Feature Importance + Model Comparison -->
            <div class="grid-2-1">
                <div>
                    ${Components.sectionHeader('📊', 'Feature Importance', 'Permutation-based ranking')}
                    <div class="chart-container">
                        ${featureImportance ? '<canvas id="fi-chart" height="300"></canvas>' : 
                            Components.emptyState('📊', 'Feature importance data not available.')}
                    </div>
                </div>
                <div>
                    ${Components.sectionHeader('🏆', 'Model Comparison', 'Ensemble vs individual')}
                    <div class="chart-container">
                        ${comparison?.models?.length ? '<canvas id="comparison-chart" height="300"></canvas>' : 
                            Components.emptyState('🏆', 'Comparison data not available.')}
                    </div>
                </div>
            </div>

            <div class="spacer-md"></div>

            <!-- Prediction Distribution -->
            ${Components.sectionHeader('📈', 'Prediction Distribution', 'Yield histogram')}
            <div class="chart-container">
                ${predictions.length ? '<canvas id="dist-chart" height="200"></canvas>' : 
                    Components.emptyState('📈', 'Make predictions to see distribution.')}
            </div>
        `;

        // Render charts
        if (featureImportance) this.renderFeatureChart(featureImportance);
        if (comparison?.models?.length) this.renderComparisonChart(comparison.models);
        if (predictions.length) this.renderDistributionChart(predictions);
    },

    renderFeatureChart(data) {
        const features = data.features || [];
        const importances = data.importances || [];
        const maxImp = Math.max(...importances, 1);
        const colors = importances.map(v => `rgba(186, 255, 41, ${0.3 + 0.7 * (v / maxImp)})`);

        Components.createChart('fi-chart', {
            type: 'bar',
            data: {
                labels: features,
                datasets: [{
                    data: importances,
                    backgroundColor: colors,
                    borderRadius: 4,
                    barThickness: 16,
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(26, 51, 80, 0.3)' }, title: { display: true, text: 'Importance' } },
                    y: { grid: { display: false } }
                }
            }
        });
    },

    renderComparisonChart(models) {
        const names = models.map(m => m.model || 'Unknown');
        const r2Scores = models.map(m => m.test_r2 || 0);

        Components.createChart('comparison-chart', {
            type: 'bar',
            data: {
                labels: names,
                datasets: [{
                    label: 'Test R²',
                    data: r2Scores,
                    backgroundColor: 'rgba(186, 255, 41, 0.7)',
                    borderRadius: 6,
                    barThickness: 28,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: 'rgba(26, 51, 80, 0.3)' }, title: { display: true, text: 'R² Score' } }
                }
            }
        });
    },

    renderDistributionChart(predictions) {
        const yields = predictions.map(p => p.predicted_yield).filter(Boolean);
        if (!yields.length) return;

        // Create histogram bins
        const min = Math.min(...yields);
        const max = Math.max(...yields);
        const binCount = 15;
        const binSize = (max - min) / binCount || 1;
        const bins = Array(binCount).fill(0);
        const labels = [];

        for (let i = 0; i < binCount; i++) {
            const lo = min + i * binSize;
            labels.push(Components.formatNumber(lo));
        }
        
        yields.forEach(y => {
            const idx = Math.min(Math.floor((y - min) / binSize), binCount - 1);
            bins[idx]++;
        });

        Components.createChart('dist-chart', {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    data: bins,
                    backgroundColor: 'rgba(186, 255, 41, 0.6)',
                    borderColor: 'rgba(186, 255, 41, 0.9)',
                    borderWidth: 1,
                    borderRadius: 3,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, title: { display: true, text: 'Predicted Yield (kg/ha)' } },
                    y: { grid: { color: 'rgba(26, 51, 80, 0.3)' }, title: { display: true, text: 'Count' } }
                }
            }
        });
    },
};

window.AnalyticsPage = AnalyticsPage;
