// Batch prediction page

const BatchPage = {
    uploadedFile: null,

    render() {
        const container = document.getElementById('page-container');
        container.innerHTML = `
            <div class="page-header">
                <h1>📁 Batch Prediction</h1>
                <p>Upload a CSV file to predict yields for multiple farms simultaneously.</p>
                <div class="chips">
                    ${Components.chip('CSV Upload')}
                    ${Components.chip('Bulk Processing')}
                    ${Components.chip('Export Results')}
                </div>
            </div>

            ${Components.sectionHeader('📤', 'Upload CSV Data', 'Drag & drop or browse')}

            <!-- Required columns info -->
            <div class="glass-panel" style="margin-bottom: 16px; border-left: 3px solid var(--accent-blue);">
                <div style="font-size: 10px; color: var(--accent-green); font-weight: 700; font-family: JetBrains Mono; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">
                    Required Columns
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                    ${['farm_area', 'temp_obs', 'wind_direction', 'dew_temp', 'pressure_sea_level', 
                       'precipitation', 'wind_speed', 'unix_sec', 'ingredient_type', 'farming_company', 
                       'deidentified_location', 'num_processing_plants'].map(c => Components.chip(c)).join('')}
                </div>
            </div>

            <!-- Drop zone -->
            <div class="file-drop-zone" id="drop-zone" onclick="document.getElementById('file-input').click()">
                <div class="drop-icon">📄</div>
                <div class="drop-text">Drop your CSV file here or click to browse</div>
                <div class="drop-hint">Supports .csv files up to 10MB</div>
                <input type="file" id="file-input" accept=".csv" style="display:none" onchange="BatchPage.onFileSelect(event)">
            </div>

            <!-- File info & results -->
            <div id="batch-content"></div>
        `;

        // Drag & drop events
        const zone = document.getElementById('drop-zone');
        zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
        zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.csv')) {
                this.handleFile(file);
            } else {
                Components.showToast('Please upload a .csv file', 'warning');
            }
        });
    },

    onFileSelect(event) {
        const file = event.target.files[0];
        if (file) this.handleFile(file);
    },

    handleFile(file) {
        this.uploadedFile = file;
        const sizeKB = (file.size / 1024).toFixed(1);
        
        const content = document.getElementById('batch-content');
        content.innerHTML = `
            <div class="spacer-md"></div>
            ${Components.sectionHeader('👀', 'File Info')}
            <div class="grid-3">
                ${Components.metricCard('File Name', file.name, '', '📄')}
                ${Components.metricCard('Size', `${sizeKB} KB`, '', '💾')}
                ${Components.metricCard('Type', 'CSV', '', '📋')}
            </div>
            <div class="spacer-md"></div>
            <button class="btn btn-primary btn-full btn-lg" onclick="BatchPage.runPrediction()">
                🚀 RUN BATCH PREDICTION
            </button>
            <div id="batch-results"></div>
        `;
    },

    async runPrediction() {
        if (!this.uploadedFile) {
            Components.showToast('Please upload a file first', 'warning');
            return;
        }

        const resultsDiv = document.getElementById('batch-results');
        resultsDiv.innerHTML = `
            <div class="spacer-md"></div>
            <div class="glass-panel" style="text-align: center;">
                <div style="margin-bottom: 12px; color: var(--text-muted);">Processing batch prediction...</div>
                ${Components.progressBar(50)}
            </div>
        `;

        try {
            const formData = new FormData();
            formData.append('file', this.uploadedFile);

            const result = await Api.predictBatch(formData);
            this.renderResults(result);
            Components.showToast(`Batch complete! ${result.total_count || 0} predictions made.`, 'success');
        } catch (error) {
            resultsDiv.innerHTML = '';
            Components.showToast(`Batch failed: ${error.message}`, 'error');
        }
    },

    renderResults(result) {
        const resultsDiv = document.getElementById('batch-results');
        const summary = result.summary || {};
        const predictions = result.predictions || [];

        resultsDiv.innerHTML = `
            <div class="spacer-md"></div>
            ${Components.sectionHeader('📊', 'Batch Results', `${result.total_count || 0} predictions`)}
            
            <div class="grid-4">
                ${Components.metricCard('Total', Components.formatNumber(result.total_count || 0), '', '📊')}
                ${Components.metricCard('Mean Yield', `${Components.formatNumber(summary.mean_yield || 0)} kg/ha`, '', '🌾')}
                ${Components.metricCard('Max Yield', `${Components.formatNumber(summary.max_yield || 0)} kg/ha`, '', '📈')}
                ${Components.metricCard('Std Dev', Components.formatNumber(summary.std_yield || 0), '', '📐')}
            </div>

            <div class="spacer-md"></div>

            <div class="grid-1-1">
                <div>
                    <div class="chart-container">
                        <canvas id="batch-dist-chart" height="250"></canvas>
                    </div>
                </div>
                <div>
                    <div class="chart-container">
                        <canvas id="batch-pie-chart" height="250"></canvas>
                    </div>
                </div>
            </div>

            <div class="spacer-md"></div>
            ${Components.sectionHeader('📋', 'Detailed Results')}
            <div class="glass-panel" style="overflow-x: auto; max-height: 400px; overflow-y: auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Predicted Yield</th>
                            <th>CI Lower</th>
                            <th>CI Upper</th>
                            <th>Category</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${predictions.slice(0, 100).map((p, i) => `
                            <tr>
                                <td>${i + 1}</td>
                                <td style="font-family: JetBrains Mono; color: var(--accent-green);">${Components.formatNumber(p.predicted_yield)}</td>
                                <td>${Components.formatNumber(p.confidence_interval_lower)}</td>
                                <td>${Components.formatNumber(p.confidence_interval_upper)}</td>
                                <td>${Components.yieldBadge(p.yield_category)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div class="spacer-md"></div>
            <button class="btn btn-secondary" onclick="BatchPage.downloadCSV(${JSON.stringify(predictions).replace(/"/g, '&quot;')})">
                📥 Download Results (CSV)
            </button>
        `;

        // Render charts
        this.renderBatchCharts(predictions, summary);
    },

    renderBatchCharts(predictions, summary) {
        const yields = predictions.map(p => p.predicted_yield).filter(Boolean);
        if (yields.length) {
            const min = Math.min(...yields);
            const max = Math.max(...yields);
            const binCount = 12;
            const binSize = (max - min) / binCount || 1;
            const bins = Array(binCount).fill(0);
            const labels = [];
            for (let i = 0; i < binCount; i++) labels.push(Components.formatNumber(min + i * binSize));
            yields.forEach(y => { bins[Math.min(Math.floor((y - min) / binSize), binCount - 1)]++; });

            Components.createChart('batch-dist-chart', {
                type: 'bar',
                data: { labels, datasets: [{ data: bins, backgroundColor: 'rgba(186, 255, 41, 0.6)', borderRadius: 3 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
                    scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(26,51,80,0.3)' } } } }
            });
        }

        const high = summary.high_yield_count || 0;
        const medium = summary.medium_yield_count || 0;
        const low = summary.low_yield_count || 0;
        Components.createChart('batch-pie-chart', {
            type: 'doughnut',
            data: { labels: ['High', 'Medium', 'Low'], datasets: [{ data: [high, medium, low], backgroundColor: ['#00E676', '#FFD600', '#FF5252'], borderColor: '#060D1A', borderWidth: 3 }] },
            options: { responsive: true, maintainAspectRatio: false, cutout: '60%', plugins: { legend: { position: 'bottom' } } }
        });
    },

    downloadCSV(predictions) {
        // Reconstruct from table if called with stringified empty
        const preds = typeof predictions === 'string' ? JSON.parse(predictions) : predictions;
        let csv = 'Row,Predicted_Yield,CI_Lower,CI_Upper,Category\n';
        preds.forEach((p, i) => {
            csv += `${i + 1},${p.predicted_yield},${p.confidence_interval_lower},${p.confidence_interval_upper},${p.yield_category}\n`;
        });
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `batch_predictions_${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    }
};

window.BatchPage = BatchPage;
