// Main SPA router (hash-based)

const App = {
    currentPage: 'dashboard',

    pages: {
        dashboard: DashboardPage,
        predictor: PredictorPage,
        analytics: AnalyticsPage,
        batch: BatchPage,
        history: HistoryPage,
    },

    init() {
        // Set up routing
        window.addEventListener('hashchange', () => this.route());
        
        // Set up mobile hamburger
        document.getElementById('hamburger')?.addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });

        // Close sidebar on nav click (mobile)
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                document.getElementById('sidebar').classList.remove('open');
            });
        });

        // Initial route
        this.route();
        
        // Health check
        this.checkHealth();
    },

    route() {
        const hash = window.location.hash.replace('#', '') || 'dashboard';
        this.currentPage = hash;
        this.setActiveNav(hash);
        this.renderPage(hash);
    },

    setActiveNav(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });
    },

    renderPage(page) {
        const pageObj = this.pages[page];
        if (pageObj) {
            // Reset container with animation
            const container = document.getElementById('page-container');
            container.style.opacity = '0';
            container.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                pageObj.render();
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            }, 100);
        } else {
            document.getElementById('page-container').innerHTML = 
                Components.emptyState('🔍', 'Page not found');
        }
    },

    async checkHealth() {
        try {
            const health = await Api.getHealth();
            const statusEl = document.getElementById('system-status');
            if (health?.model_loaded) {
                statusEl.textContent = '● Online';
                statusEl.className = 'info-value status-online';
            } else {
                statusEl.textContent = '○ Degraded';
                statusEl.style.color = 'var(--warning)';
            }
        } catch {
            const statusEl = document.getElementById('system-status');
            statusEl.textContent = '● Offline';
            statusEl.style.color = 'var(--danger)';
        }
    }
};

// Boot the app
document.addEventListener('DOMContentLoaded', () => App.init());
