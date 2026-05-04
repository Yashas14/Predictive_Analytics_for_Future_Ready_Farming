// API client — wraps fetch calls to the backend

const API_BASE = '/api/v1';

const Api = {
    async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;
        const config = {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Cannot connect to API server. Is the backend running?');
            }
            throw error;
        }
    },

    async getHealth() {
        return this.request('/health');
    },

    async predictSingle(inputData) {
        return this.request('/predict', {
            method: 'POST',
            body: JSON.stringify(inputData),
        });
    },

    async predictBatch(formData) {
        const url = `${API_BASE}/predict/batch`;
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}`);
        }
        return response.json();
    },

    async getModelMetrics() {
        return this.request('/analytics/model-metrics');
    },

    async getFeatureImportance() {
        return this.request('/analytics/feature-importance');
    },

    async getModelComparison() {
        return this.request('/analytics/model-comparison');
    },

    async getHistory(limit = 50) {
        return this.request(`/analytics/historical-predictions?limit=${limit}`);
    },
};

window.Api = Api;