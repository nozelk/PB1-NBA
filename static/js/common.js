if (typeof Chart !== 'undefined') {
Chart.defaults.color = '#a5b3c3';
Chart.defaults.borderColor = 'rgba(125, 143, 165, 0.16)';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.tooltip.backgroundColor = '#171e28';
Chart.defaults.plugins.tooltip.borderColor = '#354252';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.titleFont = { family: "'Inter', sans-serif", weight: '600' };

}

const NBA = {
    CYAN: '#83cfc5',
    BLUE: '#92b1df',
    PURPLE: '#b0a3d2',
    RED: '#ee9c9c',
    GREEN: '#97caa9',
    ORANGE: '#dbb181',
    GOLD: '#d4bb86',
    COLORS: ['#83cfc5','#92b1df','#b0a3d2','#ee9c9c','#97caa9','#dbb181','#d4bb86','#c49eb5','#b3c793'],

    async fetchJSON(url) {
        try {
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return await res.json();
        } catch (err) {
            console.error('Fetch error:', url, err);
            return null;
        }
    },

    showLoading(el) {
        el.innerHTML = `<div class="text-center py-5">
            <div class="spinner-border" style="color:var(--accent-cyan);" role="status"></div>
            <p class="mt-2" style="color:var(--text-secondary);font-size:0.85rem;">Loading data...</p>
        </div>`;
    },

    showError(el, msg) {
        el.innerHTML = `<div class="text-center py-5">
            <i class="bi bi-exclamation-triangle" style="font-size:2rem;color:var(--accent-red);"></i>
            <p class="mt-2" style="color:var(--text-secondary);">${msg || 'Failed to load data'}</p>
        </div>`;
    },

    count(n) {
        if (n == null || !Number.isFinite(Number(n))) return '—';
        return new Intl.NumberFormat('en-US', {maximumFractionDigits: 0}).format(Number(n));
    },

    escape(value) {
        return String(value ?? '').replace(/[&<>"']/g, ch =>
            ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));
    },

    fmt(n, d=1) {
        if (n == null) return '-';
        return parseFloat(n).toFixed(d);
    },

    createGradient(ctx, c) {
        const g = ctx.createLinearGradient(0, 0, 0, 400);
        g.addColorStop(0, c + '80');
        g.addColorStop(1, c + '05');
        return g;
    }
};

// Global search
const searchInput = document.getElementById('globalSearch');
const searchResults = document.getElementById('searchResults');
let searchTimeout;

searchInput?.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    const q = searchInput.value.trim();
    if (q.length < 2) { searchResults.classList.remove('active'); return; }
    searchTimeout = setTimeout(async () => {
        const data = await NBA.fetchJSON(`/api/search?q=${encodeURIComponent(q)}`);
        if (!data) return;
        let h = '';
        if (data.players?.length) {
            h += '<div style="padding:8px 15px;color:var(--accent-cyan);font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">Players</div>';
            data.players.forEach(p => {
                h += `<a href="/player/${p.player_id}" class="search-result-item">
                    <i class="bi bi-person" style="color:var(--accent-cyan);"></i>
                    <span>${p.full_name}</span></a>`;
            });
        }
        if (data.teams?.length) {
            h += '<div style="padding:8px 15px;color:var(--accent-cyan);font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">Teams</div>';
            data.teams.forEach(t => {
                h += `<a href="/team/${t.team_id}" class="search-result-item">
                    <img src="/team/logo/${encodeURIComponent(t.full_name)}" alt="" style="width:24px;height:24px;object-fit:contain;">
                    <span>${t.full_name}</span></a>`;
            });
        }
        if (!h) h = '<div class="search-result-item" style="color:var(--text-muted);">No results found</div>';
        searchResults.innerHTML = h;
        searchResults.classList.add('active');
    }, 300);
});

document.addEventListener('click', e => {
    if (!searchResults?.contains(e.target) && e.target !== searchInput)
        searchResults?.classList.remove('active');
});
