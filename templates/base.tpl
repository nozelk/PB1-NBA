<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ get('title', 'NBA Analytics') }} | NBA Analytics</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Oswald:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <!-- Custom CSS -->
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid px-3">
            <a class="navbar-brand" href="/">
                <i class="bi bi-dribbble" style="color: var(--accent-cyan); font-size: 1.6rem;"></i>
                <span class="brand-text">NBA Analytics</span>
            </a>

            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#mainNav">
                <i class="bi bi-list" style="color: var(--accent-cyan); font-size: 1.5rem;"></i>
            </button>

            <div class="collapse navbar-collapse" id="mainNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if get('page', '') == 'home' else '' }}" href="/">
                            <i class="bi bi-house-door me-1"></i>Home
                        </a>
                    </li>
                </ul>


            </div>
        </div>
    </nav>

    <!-- MAIN CONTENT -->
    <main>
        {{!base}}
    </main>

    <!-- FOOTER -->
    <footer style="background: var(--bg-secondary); border-top: 1px solid var(--border); padding: 1.5rem 0; margin-top: 3rem;">
        <div class="container-fluid px-4 text-center">
            <span style="color: var(--text-muted); font-size: 0.8rem;">
                NBA Analytics Dashboard &middot; Data from <a href="https://www.nba.com" target="_blank">NBA.com</a> via nba_api
            </span>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Chart.js default config for dark theme -->
    <script>
        Chart.defaults.color = '#8888aa';
        Chart.defaults.borderColor = 'rgba(42, 42, 68, 0.5)';
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.tooltip.backgroundColor = '#1a1a2e';
        Chart.defaults.plugins.tooltip.borderColor = '#2a2a44';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.titleFont = { family: "'Oswald', sans-serif", weight: '600' };

        const NBA = {
            CYAN: '#00f0ff',
            BLUE: '#4361ee',
            PURPLE: '#7b2ff7',
            RED: '#ff2d55',
            GREEN: '#00e676',
            ORANGE: '#ff9100',
            GOLD: '#ffd700',
            COLORS: ['#00f0ff','#4361ee','#7b2ff7','#ff2d55','#00e676','#ff9100','#ffd700','#e040fb','#76ff03'],

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
                            <img src="/static/images/logos/${t.abbreviation}.png" alt="" style="width:24px;height:24px;object-fit:contain;">
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
    </script>
</body>
</html>