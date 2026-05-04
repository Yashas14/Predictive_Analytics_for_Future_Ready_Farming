// Shared UI components (HTML generators + utility fns)

const Components = {
    metricCard(label, value, delta = '', icon = '') {
        return `
        <div class="metric-card">
            ${icon ? `<div class="card-icon">${icon}</div>` : ''}
            <div class="card-label">${label}</div>
            <div class="card-value">${value}</div>
            ${delta ? `<div class="card-delta">${delta}</div>` : ''}
        </div>`;
    },

    sectionHeader(icon, title, subtitle = '') {
        return `
        <div class="section-header">
            <span class="header-icon">${icon}</span>
            <span class="header-title">${title}</span>
            ${subtitle ? `<span class="header-subtitle">${subtitle}</span>` : ''}
        </div>`;
    },

    yieldBadge(category) {
        const icons = { high: '▲', medium: '●', low: '▼' };
        const labels = { high: 'HIGH YIELD', medium: 'MEDIUM YIELD', low: 'LOW YIELD' };
        const cls = category || 'medium';
        return `<span class="yield-badge ${cls}">${icons[cls] || '●'} ${labels[cls] || 'UNKNOWN'}</span>`;
    },

    loading(text = 'Loading...') {
        return `
        <div class="loading-overlay">
            <div class="spinner"></div>
            <span>${text}</span>
        </div>`;
    },

    emptyState(icon, text) {
        return `
        <div class="empty-state">
            <div class="empty-icon">${icon}</div>
            <div class="empty-text">${text}</div>
        </div>`;
    },

    chip(text) {
        return `<span class="chip">${text}</span>`;
    },

    statPill(text) {
        return `<span class="stat-pill">${text}</span>`;
    },

    progressBar(percent) {
        return `
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${percent}%"></div>
        </div>`;
    },

    showToast(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toast-container');
        const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span><span>${message}</span>`;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100px)';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    formatNumber(num, decimals = 0) {
        if (num == null || isNaN(num)) return 'N/A';
        return Number(num).toLocaleString('en-US', { 
            minimumFractionDigits: decimals, 
            maximumFractionDigits: decimals 
        });
    },

    createChart(canvasId, config) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        Chart.defaults.color = '#7A9BB5';
        Chart.defaults.borderColor = 'rgba(26, 51, 80, 0.4)';
        Chart.defaults.font.family = "'Inter', sans-serif";
        
        return new Chart(ctx, config);
    },
};

window.Components = Components;