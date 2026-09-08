% rebase('base.tpl', title='Dashboard', page='home')

<div class="page-container">
    <!-- Hero -->
    <div style="text-align:center; margin-bottom:2.5rem;">
        <h1 style="font-size:2.5rem;">
            <span style="background:var(--gradient-main);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                NBA Analytics
            </span>
        </h1>
        <p style="color:var(--text-secondary);font-size:0.95rem;max-width:600px;margin:0.5rem auto 0;">
            Live Season Data &middot; Teams, Players, Coaches, Games &amp; Advanced Stats
        </p>
    </div>

    <!-- ★ TOP RATED PLAYERS – PER (Player Efficiency Rating) -->
    <div class="section-header" style="margin-bottom:1rem;">
        <h2><span class="section-icon"></span>Top Rated Players <span style="font-size:0.55em;color:var(--text-muted);font-weight:400;">PER</span></h2>
    </div>
    <div id="topRatedContainer" class="mb-4" style="display:flex;gap:0.75rem;overflow-x:auto;padding-bottom:0.5rem;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;">
        <div class="skeleton skeleton-card" style="min-width:200px;height:220px;"></div>
        <div class="skeleton skeleton-card" style="min-width:200px;height:220px;"></div>
        <div class="skeleton skeleton-card" style="min-width:200px;height:220px;"></div>
    </div>

    <!-- ★ BEST PERFORMANCES (day/week/month tabs) -->
    <div class="mb-4" id="perfSection">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2" style="margin-bottom:1rem;">
            <h5 style="margin:0;font-family:var(--font-display);letter-spacing:1.5px;text-transform:uppercase;font-size:0.85rem;color:var(--accent-cyan);"><i class="bi bi-fire me-2" style="color:var(--accent-red);"></i>Best Performances</h5>
            <div class="nav-tabs-nba" style="margin:0;">
                <button class="tab-btn perf-period active" data-period="day">Today</button>
                <button class="tab-btn perf-period" data-period="week">This Week</button>
                <button class="tab-btn perf-period" data-period="month">This Month</button>
                <button class="tab-btn perf-period" data-period="season">Season</button>
            </div>
        </div>
        <div id="perfBody" style="display:flex;gap:0.75rem;overflow-x:auto;padding-bottom:0.5rem;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;">
            <div class="skeleton skeleton-card" style="min-width:200px;height:220px;"></div>
            <div class="skeleton skeleton-card" style="min-width:200px;height:220px;"></div>
            <div class="skeleton skeleton-card" style="min-width:200px;height:220px;"></div>
        </div>
    </div>

    <!-- ★ RECENT GAMES + AWARDS | STANDINGS -->
    <div class="row g-4 mb-4">
        <div class="col-lg-5 d-flex flex-column gap-3">
            <div class="card">
                <div class="card-header">
                    <h5><i class="bi bi-controller me-2"></i>Recent Games</h5>
                </div>
                <div class="card-body" id="recentGamesBody">
                    <div class="skeleton skeleton-card" style="height:300px;"></div>
                </div>
            </div>

            <!-- Season Awards -->
            <div id="powSection" class="card" style="display:none;flex:1;">
                <div class="card-header" style="padding:.55rem .75rem;">
                    <h5 style="font-size:.85rem;margin:0;"><i class="bi bi-trophy-fill me-2" style="color:var(--accent-gold);"></i>Season Awards</h5>
                </div>
                <div class="card-body" style="padding:.5rem;" id="powGrid"></div>
            </div>
        </div>

        <!-- Standings -->
        <div class="col-lg-7 d-flex flex-column gap-3">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5><i class="bi bi-bar-chart me-2"></i>Standings</h5>
                    <select id="standingsSeason" class="form-select" style="width:auto;padding:4px 30px 4px 12px;font-size:0.8rem;"></select>
                </div>
                <div class="card-body" id="standingsBody">
                    <div class="skeleton skeleton-card"></div>
                </div>
            </div>

            <!-- Division Leaders -->
            <div id="divLeadersSection" class="card" style="display:none;">
                <div class="card-header" style="padding:.55rem .75rem;">
                    <h5 style="font-size:.85rem;margin:0;"><i class="bi bi-flag-fill me-2" style="color:var(--accent-green);"></i>Division Leaders</h5>
                </div>
                <div class="card-body" style="padding:.5rem;" id="divLeadersGrid"></div>
            </div>
        </div>
    </div>

    <!-- Leaderboards row (Scorers / Assists / Rebounds / Steals) -->
    <div class="row g-4 mb-4">
        <div class="col-lg-3">
            <div class="card h-100">
                <div class="card-header">
                    <h5 style="margin:0;"><i class="bi bi-trophy me-2" style="color:var(--accent-cyan);"></i>Top Scorers</h5>
                </div>
                <div class="card-body" id="topScorersBody" style="max-height:400px;overflow-y:auto;">
                    <div class="skeleton skeleton-card"></div>
                </div>
            </div>
        </div>
        <div class="col-lg-3">
            <div class="card h-100">
                <div class="card-header">
                    <h5 style="margin:0;"><i class="bi bi-hand-index me-2" style="color:var(--accent-blue);"></i>Top Assists</h5>
                </div>
                <div class="card-body" id="topAssistsBody" style="max-height:400px;overflow-y:auto;">
                    <div class="skeleton skeleton-card"></div>
                </div>
            </div>
        </div>
        <div class="col-lg-3">
            <div class="card h-100">
                <div class="card-header">
                    <h5 style="margin:0;"><i class="bi bi-arrow-repeat me-2" style="color:var(--accent-purple);"></i>Top Rebounds</h5>
                </div>
                <div class="card-body" id="topReboundsBody" style="max-height:400px;overflow-y:auto;">
                    <div class="skeleton skeleton-card"></div>
                </div>
            </div>
        </div>
        <div class="col-lg-3">
            <div class="card h-100">
                <div class="card-header">
                    <h5 style="margin:0;"><i class="bi bi-shield-check me-2" style="color:var(--accent-green);"></i>Top Steals</h5>
                </div>
                <div class="card-body" id="topStealsBody" style="max-height:400px;overflow-y:auto;">
                    <div class="skeleton skeleton-card"></div>
                </div>
            </div>
        </div>
    </div>

    <!-- Charts row -->
    <div class="row g-4 mb-4">
        <div class="col-lg-6">
            <div class="chart-container">
                <h5 style="color:var(--accent-cyan);font-family:var(--font-display);font-size:0.85rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:1rem;">
                    <i class="bi bi-graph-up me-2"></i>League Avg PPG by Season
                </h5>
                <canvas id="chartPPG" height="200"></canvas>
            </div>
        </div>
        <div class="col-lg-6">
            <div class="chart-container">
                <h5 style="color:var(--accent-cyan);font-family:var(--font-display);font-size:0.85rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:1rem;">
                    <i class="bi bi-bullseye me-2"></i>League Avg 3PT% by Season
                </h5>
                <canvas id="chart3PT" height="200"></canvas>
            </div>
        </div>
    </div>

    <!-- Quick links -->
    <div class="row g-3">
        <div class="col-md-3 col-6">
            <a href="/team/" class="card text-center" style="text-decoration:none;">
                <div class="card-body py-4">
                    <i class="bi bi-people" style="font-size:2rem;color:var(--accent-cyan);"></i>
                    <div style="margin-top:0.5rem;font-family:var(--font-display);letter-spacing:1px;text-transform:uppercase;font-size:0.85rem;">Teams</div>
                </div>
            </a>
        </div>
        <div class="col-md-3 col-6">
            <a href="/player/" class="card text-center" style="text-decoration:none;">
                <div class="card-body py-4">
                    <i class="bi bi-person" style="font-size:2rem;color:var(--accent-blue);"></i>
                    <div style="margin-top:0.5rem;font-family:var(--font-display);letter-spacing:1px;text-transform:uppercase;font-size:0.85rem;">Players</div>
                </div>
            </a>
        </div>
        <div class="col-md-3 col-6">
            <a href="/games/" class="card text-center" style="text-decoration:none;">
                <div class="card-body py-4">
                    <i class="bi bi-calendar-event" style="font-size:2rem;color:var(--accent-purple);"></i>
                    <div style="margin-top:0.5rem;font-family:var(--font-display);letter-spacing:1px;text-transform:uppercase;font-size:0.85rem;">Games</div>
                </div>
            </a>
        </div>
        <div class="col-md-3 col-6">
            <a href="/compare" class="card text-center" style="text-decoration:none;">
                <div class="card-body py-4">
                    <i class="bi bi-arrow-left-right" style="font-size:2rem;color:var(--accent-orange);"></i>
                    <div style="margin-top:0.5rem;font-family:var(--font-display);letter-spacing:1px;text-transform:uppercase;font-size:0.85rem;">Compare</div>
                </div>
            </a>
        </div>
    </div>
</div>

<script>
function seasonLabel(y) {
    const n = parseInt(y, 10);
    if (isNaN(n)) return y;
    const next = ((n + 1) % 100).toString().padStart(2, '0');
    return n + '/' + next;
}

document.addEventListener('DOMContentLoaded', async () => {
    // Load seasons for selector
    const seasons = await NBA.fetchJSON('/api/seasons');
    const sel = document.getElementById('standingsSeason');
    if (seasons) {
        seasons.forEach((s, i) => {
            const opt = document.createElement('option');
            opt.value = s; opt.text = seasonLabel(s);
            if (i === 0) opt.selected = true;
            sel.appendChild(opt);
        });
    }

    // ── Load dashboard ──────────────────────────
    const data = await NBA.fetchJSON('/api/dashboard');
    if (data) {
        // Leaderboards — scorers / assists / rebounds
        renderLeaderboard('topScorersBody', data.top_scorers, 'ppg', 'PPG', 'var(--accent-cyan)');
        renderLeaderboard('topAssistsBody', data.top_assists, 'apg', 'APG', 'var(--accent-blue)');
        renderLeaderboard('topReboundsBody', data.top_rebounds, 'rpg', 'RPG', 'var(--accent-purple)');
        renderLeaderboard('topStealsBody', data.top_steals, 'spg', 'SPG', 'var(--accent-green)');

        // Standings
        loadStandings(sel.value);
        sel.addEventListener('change', () => loadStandings(sel.value));

        // Division Leaders
        renderDivisionLeaders(data.division_leaders);

        // Charts
        if (data.league_trends && data.league_trends.length) {
            const labels = data.league_trends.map(t => seasonLabel(t.season));
            const ppgData = data.league_trends.map(t => t.avg_ppg);
            const fg3Data = data.league_trends.map(t => t.avg_fg3_pct ? (t.avg_fg3_pct * 100).toFixed(1) : null);

            const ctx1 = document.getElementById('chartPPG').getContext('2d');
            new Chart(ctx1, {
                type: 'line',
                data: { labels, datasets: [{ label: 'Avg PPG', data: ppgData, borderColor: NBA.CYAN, backgroundColor: NBA.createGradient(ctx1, NBA.CYAN), fill: true, tension: 0.4, pointRadius: 3, pointHoverRadius: 6 }] },
                options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(42,42,68,0.3)' } }, x: { grid: { display: false } } } }
            });

            const ctx2 = document.getElementById('chart3PT').getContext('2d');
            new Chart(ctx2, {
                type: 'line',
                data: { labels, datasets: [{ label: 'Avg 3PT%', data: fg3Data, borderColor: NBA.PURPLE, backgroundColor: NBA.createGradient(ctx2, NBA.PURPLE), fill: true, tension: 0.4, pointRadius: 3, pointHoverRadius: 6 }] },
                options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(42,42,68,0.3)' }, ticks: { callback: v => v+'%' } }, x: { grid: { display: false } } } }
            });
        }
    }

    // ── Top Rated Players ──────────────────────────
    loadTopRated();

    // ── Best Performances (default: today) ──────────
    loadPerformances('day');
    document.querySelectorAll('.perf-period').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.perf-period').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadPerformances(btn.dataset.period);
        });
    });

    // ── Recent Games ──────────────────────────
    loadRecentGames();

    // ── Player of the Week ──────────────────────
    loadPlayerOfWeek();
});

// ── LEADERBOARD RENDERER ──────────────────────
function renderLeaderboard(elId, list, statKey, statLabel, color) {
    const el = document.getElementById(elId);
    if (!list || !list.length) { el.innerHTML = '<p style="color:var(--text-muted);">No data</p>'; return; }
    el.innerHTML = list.map((p, i) =>
        `<a href="/player/${p.player_id}" class="standings-row animate-in" style="text-decoration:none;color:inherit;">
            <span class="rank-num">${i+1}</span>
            <span style="flex:1;font-size:0.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.full_name}</span>
            <span style="font-size:0.7rem;color:var(--text-muted);margin-right:6px;">${p.abbreviation || ''}</span>
            <span class="num" style="color:${color};font-weight:600;">${NBA.fmt(p[statKey])}</span>
            <span style="color:var(--text-muted);font-size:0.65rem;margin-left:2px;">${statLabel}</span>
        </a>`
    ).join('');
}

// ── TOP RATED ──────────────────────────────────
async function loadTopRated() {
    const el = document.getElementById('topRatedContainer');
    const data = await NBA.fetchJSON('/api/top-rated?limit=10');
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No data yet. Run data collection first.</p>'; return; }

    // Color for PER badge
    function perColor(v) {
        if (v >= 30) return 'var(--accent-cyan)';
        if (v >= 25) return 'var(--accent-blue)';
        if (v >= 20) return 'var(--accent-purple)';
        if (v >= 15) return 'var(--accent-orange)';
        return 'var(--text-muted)';
    }

    const borderColors = [
        'var(--accent-cyan)','var(--accent-blue)','var(--accent-purple)',
        'var(--accent-orange)','var(--accent-green)',
        'var(--border-color)','var(--border-color)','var(--border-color)','var(--border-color)','var(--border-color)'
    ];
    const medals = ['🥇','🥈','🥉','4️⃣','5️⃣'];

    el.innerHTML = data.map((p, i) => {
        const rankLabel = i < 5 ? `<div style="font-size:1.3rem;margin-bottom:2px;">${medals[i]}</div>` : `<div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--text-muted);margin-bottom:2px;">#${i+1}</div>`;
        const tsPct = p.ts_pct ? (p.ts_pct * 100).toFixed(1) + '%' : '-';
        const winPct = p.team_win_pct ? (p.team_win_pct * 100).toFixed(0) + '%' : '-';
        const pmStr = p.pm_per36 != null ? (p.pm_per36 > 0 ? '+' : '') + p.pm_per36 : '-';
        const pmColor = p.pm_per36 > 0 ? 'var(--accent-green)' : p.pm_per36 < 0 ? 'var(--accent-red)' : 'var(--text-muted)';
        return `<a href="/player/${p.player_id}" class="card animate-in" style="min-width:200px;max-width:230px;flex:0 0 auto;text-decoration:none;border-color:${borderColors[i]};overflow:hidden;">
            <div style="text-align:center;padding:1rem 0.75rem 0.75rem;">
                <div style="width:56px;height:56px;border-radius:50%;background:var(--bg-secondary);margin:0 auto 0.5rem;display:flex;align-items:center;justify-content:center;border:2px solid ${borderColors[i]};overflow:hidden;">
                    <img src="https://cdn.nba.com/headshots/nba/latest/260x190/${p.player_id}.png"
                         style="width:100%;height:100%;object-fit:cover;"
                         onerror="this.parentElement.innerHTML='<i class=\\'bi bi-person\\' style=\\'font-size:1.5rem;color:var(--text-muted);\\'></i>'">
                </div>
                ${rankLabel}
                <div style="font-family:var(--font-display);font-size:0.82rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.full_name}</div>
                <div style="font-size:0.68rem;color:var(--text-muted);margin-bottom:0.4rem;">${p.team_abbreviation} &middot; ${p.position || ''} &middot; ${p.gp}GP</div>
                <div style="font-family:var(--font-mono);font-size:1.5rem;color:${perColor(p.per)};font-weight:700;">${NBA.fmt(p.per, 2)}</div>
                <div style="font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">PER</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px 4px;font-size:0.7rem;margin-bottom:0.4rem;">
                    <div><span class="num" style="color:var(--accent-cyan);font-weight:700;font-size:0.9rem;">${NBA.fmt(p.ppg)}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">PPG</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${NBA.fmt(p.rpg)}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">RPG</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${NBA.fmt(p.apg)}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">APG</span></div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px 4px;font-size:0.65rem;">
                    <div><span class="num" style="color:var(--text-primary);">${tsPct}</span><br><span style="color:var(--text-muted);font-size:0.55rem;">TS%</span></div>
                    <div><span class="num" style="color:${pmColor};">${pmStr}</span><br><span style="color:var(--text-muted);font-size:0.55rem;">+/-36</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${winPct}</span><br><span style="color:var(--text-muted);font-size:0.55rem;">W%</span></div>
                </div>
            </div>
        </a>`;
    }).join('');

    enableDragScroll(el);
}

// ── BEST PERFORMANCES ──────────────────────────
async function loadPerformances(period) {
    const section = document.getElementById('perfSection');
    const el = document.getElementById('perfBody');
    NBA.showLoading(el);
    const data = await NBA.fetchJSON(`/api/best-performances?period=${period}&limit=10`);
    if (!data || !data.length) {
        section.style.display = 'none';
        return;
    }
    section.style.display = '';
    el.style.display = 'flex';

    const borderColors = [
        'var(--accent-cyan)','var(--accent-blue)','var(--accent-purple)',
        'var(--accent-orange)','var(--accent-green)',
        'var(--border-color)','var(--border-color)','var(--border-color)','var(--border-color)','var(--border-color)'
    ];
    const medals = ['🥇','🥈','🥉','4️⃣','5️⃣'];

    el.innerHTML = data.map((p, i) => {
        const wlColor = p.wl === 'W' ? 'var(--accent-green)' : 'var(--accent-red)';
        const rankLabel = i < 5 ? `<div style="font-size:1.3rem;margin-bottom:2px;">${medals[i]}</div>` : `<div style="font-family:var(--font-mono);font-size:0.85rem;color:var(--text-muted);margin-bottom:2px;">#${i+1}</div>`;
        const fgPct = p.fg_pct != null ? (p.fg_pct * 100).toFixed(0) + '%' : '-';
        const pm = p.plus_minus != null ? (p.plus_minus > 0 ? '+' : '') + parseInt(p.plus_minus) : '-';
        const pmColor = p.plus_minus > 0 ? 'var(--accent-green)' : p.plus_minus < 0 ? 'var(--accent-red)' : 'var(--text-muted)';
        return `<a href="/player/${p.player_id}" class="card animate-in" style="min-width:195px;max-width:220px;flex:0 0 auto;text-decoration:none;border-color:${borderColors[i]};overflow:hidden;">
            <div style="text-align:center;padding:1rem 0.75rem 0.75rem;">
                <div style="width:56px;height:56px;border-radius:50%;background:var(--bg-secondary);margin:0 auto 0.5rem;display:flex;align-items:center;justify-content:center;border:2px solid ${borderColors[i]};overflow:hidden;">
                    <img src="https://cdn.nba.com/headshots/nba/latest/260x190/${p.player_id}.png"
                         style="width:100%;height:100%;object-fit:cover;"
                         onerror="this.parentElement.innerHTML='<i class=\\'bi bi-person\\' style=\\'font-size:1.5rem;color:var(--text-muted);\\'></i>'">
                </div>
                ${rankLabel}
                <div style="font-family:var(--font-display);font-size:0.82rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.full_name}</div>
                <div style="font-size:0.68rem;color:var(--text-muted);margin-bottom:0.4rem;">${p.team_abbreviation || ''} &middot; <span style="color:${wlColor};font-weight:600;">${p.wl || ''}</span> &middot; ${p.game_date || ''}</div>
                <div style="font-family:var(--font-mono);font-size:1.3rem;color:var(--accent-cyan);font-weight:700;">${NBA.fmt(p.game_score)}</div>
                <div style="font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">Game Score</div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:2px 4px;font-size:0.7rem;">
                    <div><span class="num" style="color:var(--accent-cyan);font-weight:700;font-size:0.95rem;">${parseInt(p.pts)||0}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">PTS</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${parseInt(p.reb)||0}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">REB</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${parseInt(p.ast)||0}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">AST</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${parseInt(p.stl)||0}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">STL</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${parseInt(p.blk)||0}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">BLK</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${parseInt(p.tov)||0}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">TOV</span></div>
                    <div><span class="num" style="color:var(--text-primary);">${fgPct}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">FG%</span></div>
                    <div><span class="num" style="color:${pmColor};">${pm}</span><br><span style="color:var(--text-muted);font-size:0.6rem;">+/-</span></div>
                </div>
            </div>
        </a>`;
    }).join('');

    // Enable horizontal drag-scroll
    enableDragScroll(el);
}

// ── RECENT GAMES ──────────────────────────
async function loadRecentGames() {
    const el = document.getElementById('recentGamesBody');
    const data = await NBA.fetchJSON('/api/recent-games?limit=8');
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No game data yet.</p>'; return; }

    el.innerHTML = data.map(g => {
        const homeWin = g.home_pts > (g.away_pts || 0);
        return `<div class="standings-row animate-in" style="align-items:center;">
            <div style="flex:1;text-align:right;">
                <a href="/team/${g.home_team_id}" style="color:${homeWin ? 'var(--text-primary)' : 'var(--text-muted)'};text-decoration:none;font-weight:${homeWin ? '700' : '400'};font-size:0.85rem;">
                    ${g.home_team}
                </a>
            </div>
            <div style="min-width:80px;text-align:center;font-family:var(--font-mono);font-size:0.9rem;">
                <span style="color:${homeWin ? 'var(--accent-cyan)' : 'var(--text-muted)'};">${g.home_pts || 0}</span>
                <span style="color:var(--text-muted);margin:0 4px;">-</span>
                <span style="color:${!homeWin ? 'var(--accent-cyan)' : 'var(--text-muted)'};">${g.away_pts || 0}</span>
            </div>
            <div style="flex:1;">
                <a href="/team/${g.away_team_id}" style="color:${!homeWin ? 'var(--text-primary)' : 'var(--text-muted)'};text-decoration:none;font-weight:${!homeWin ? '700' : '400'};font-size:0.85rem;">
                    ${g.away_team}
                </a>
            </div>
            <div style="font-size:0.7rem;color:var(--text-muted);min-width:70px;text-align:right;">${g.game_date || ''}</div>
        </div>`;
    }).join('');
}

// ── STANDINGS ──────────────────────────
async function loadStandings(season) {
    const body = document.getElementById('standingsBody');
    NBA.showLoading(body);
    const data = await NBA.fetchJSON(`/api/dashboard?season=${season}`);
    if (!data || !data.standings) { NBA.showError(body); return; }

    const east = data.standings.filter(t => t.conference === 'East');
    const west = data.standings.filter(t => t.conference === 'West');

    body.innerHTML = '<div class="conference-split">' + buildConf('Eastern', east) + buildConf('Western', west) + '</div>';
}

function buildConf(name, teams) {
    let h = `<div>
        <div style="color:var(--accent-cyan);font-family:var(--font-display);font-size:0.75rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.75rem;">${name}</div>`;
    teams.forEach((t, i) => {
        h += `<a href="/team/${t.team_id}" class="standings-row" style="text-decoration:none;color:inherit;">
            <span class="rank-num">${i+1}</span>
            <img class="team-logo-sm" src="/static/images/logos/${t.abbreviation}.png" alt="${t.abbreviation}" onerror="this.style.display='none'">
            <span style="flex:1;font-size:0.8rem;">${t.abbreviation}</span>
            <span class="record num">${t.wins}-${t.losses}</span>
        </a>`;
    });
    return h + '</div>';
}

// ── SEASON AWARDS ──────────────────────────
async function loadPlayerOfWeek() {
    const data = await NBA.fetchJSON('/api/player-of-the-week');
    if (!data) return;

    const keys = ['pow_east','pow_west','pom_east','pom_west','dpom_east','dpom_west','rom_east','rom_west'];
    if (!keys.some(k => data[k])) return;

    const section = document.getElementById('powSection');
    const grid = document.getElementById('powGrid');
    section.style.display = '';

    function statLine(p) {
        if (p.ppg == null) return '';
        return `<div style="display:flex;gap:8px;margin-top:4px;">
            <span style="font-size:0.7rem;color:var(--accent-cyan);font-family:var(--font-mono);">${NBA.fmt(p.ppg)} <span style="color:var(--text-muted);font-size:0.6rem;">PPG</span></span>
            <span style="font-size:0.7rem;color:var(--accent-green);font-family:var(--font-mono);">${NBA.fmt(p.rpg)} <span style="color:var(--text-muted);font-size:0.6rem;">RPG</span></span>
            <span style="font-size:0.7rem;color:var(--accent-purple);font-family:var(--font-mono);">${NBA.fmt(p.apg)} <span style="color:var(--text-muted);font-size:0.6rem;">APG</span></span>
        </div>`;
    }

    function card(p, awardLabel, confLabel, accent) {
        if (!p) return '';
        return `<a href="/player/${p.player_id}" class="animate-in" style="text-decoration:none;display:flex;align-items:center;gap:10px;padding:0.5rem 0.6rem;border-radius:8px;background:var(--bg-secondary);border:1px solid var(--border-color);transition:border-color .2s,background .2s;" onmouseenter="this.style.borderColor='${accent}';this.style.background='rgba(255,255,255,0.04)'" onmouseleave="this.style.borderColor='var(--border-color)';this.style.background='var(--bg-secondary)'">
            <div style="width:48px;height:48px;border-radius:50%;overflow:hidden;flex-shrink:0;border:2px solid ${accent};background:var(--bg-primary);display:flex;align-items:center;justify-content:center;">
                <img src="https://cdn.nba.com/headshots/nba/latest/260x190/${p.player_id}.png"
                     style="width:100%;height:100%;object-fit:cover;"
                     onerror="this.parentElement.innerHTML='<i class=\\'bi bi-person\\' style=\\'font-size:1.1rem;color:var(--text-muted);\\'></i>'">
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:0.55rem;color:${accent};text-transform:uppercase;letter-spacing:0.5px;font-family:var(--font-display);line-height:1.2;">${awardLabel} &middot; ${confLabel}</div>
                <div style="font-family:var(--font-display);font-size:0.82rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.3;">${p.full_name}</div>
                <div style="display:flex;align-items:center;gap:6px;">
                    <span style="font-size:0.65rem;color:var(--text-muted);">${p.team_abbreviation}</span>
                    ${statLine(p)}
                </div>
            </div>
        </a>`;
    }

    // Group awards into pairs (East / West per award type)
    const groups = [
        { label: 'Player of the Week', short: 'POW', e: data.pow_east, w: data.pow_west, accent: ['var(--accent-cyan)', 'var(--accent-purple)'] },
        { label: 'Player of the Month', short: 'POM', e: data.pom_east, w: data.pom_west, accent: ['var(--accent-cyan)', 'var(--accent-purple)'] },
        { label: 'Def. Player of Month', short: 'DPOM', e: data.dpom_east, w: data.dpom_west, accent: ['var(--accent-green)', 'var(--accent-gold)'] },
        { label: 'Rookie of the Month', short: 'ROTM', e: data.rom_east, w: data.rom_west, accent: ['var(--accent-cyan)', 'var(--accent-red)'] },
    ].filter(g => g.e || g.w);

    let html = '';
    for (const g of groups) {
        html += `<div style="margin-bottom:0.4rem;">
            <div style="font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px;font-family:var(--font-display);margin-bottom:0.25rem;padding-left:4px;">${g.label}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                ${card(g.e, g.short, 'East', g.accent[0])}
                ${card(g.w, g.short, 'West', g.accent[1])}
            </div>
        </div>`;
    }
    grid.innerHTML = html;
}

// ── DIVISION LEADERS ──────────────────────────
function renderDivisionLeaders(leaders) {
    if (!leaders || !leaders.length) return;
    const section = document.getElementById('divLeadersSection');
    const grid = document.getElementById('divLeadersGrid');
    section.style.display = '';

    // Sort: East divisions first, then West
    const divOrder = ['Atlantic','Central','Southeast','Northwest','Pacific','Southwest'];
    leaders.sort((a, b) => divOrder.indexOf(a.division) - divOrder.indexOf(b.division));

    const eastDivs = leaders.filter(l => l.conference === 'East');
    const westDivs = leaders.filter(l => l.conference === 'West');

    function row(t) {
        const logoSrc = t.logo_path ? '/static/images/' + t.logo_path : '';
        const record = `${t.wins}-${t.losses}`;
        const pct = t.win_pct != null ? `(.${Math.round(t.win_pct * 1000).toString().padStart(3,'0')})` : '';
        return `<a href="/team/${t.team_id}" style="text-decoration:none;display:flex;align-items:center;gap:10px;padding:0.5rem 0.6rem;border-radius:6px;background:var(--bg-secondary);border:1px solid var(--border-color);transition:border-color .2s,background .2s;" onmouseenter="this.style.borderColor='var(--accent-cyan)';this.style.background='rgba(255,255,255,0.04)'" onmouseleave="this.style.borderColor='var(--border-color)';this.style.background='var(--bg-secondary)'">
            <div style="width:36px;height:36px;flex-shrink:0;display:flex;align-items:center;justify-content:center;">
                ${logoSrc ? `<img src="${logoSrc}" style="width:100%;height:100%;object-fit:contain;" onerror="this.style.display='none'">` : ''}
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:0.55rem;color:var(--text-muted);font-family:var(--font-display);text-transform:uppercase;letter-spacing:.5px;line-height:1;">${t.division}</div>
                <div style="font-family:var(--font-display);font-size:0.8rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.3;">${t.full_name}</div>
            </div>
            <div style="text-align:right;flex-shrink:0;">
                <div style="font-family:var(--font-mono);font-size:0.8rem;color:var(--text-primary);font-weight:600;">${record}</div>
                <div style="font-size:0.6rem;color:var(--text-muted);font-family:var(--font-mono);">${pct}</div>
            </div>
        </a>`;
    }

    grid.innerHTML = `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
            <div>
                <div style="font-size:0.6rem;color:var(--accent-cyan);text-transform:uppercase;letter-spacing:1px;font-family:var(--font-display);margin-bottom:0.25rem;padding-left:4px;">Eastern</div>
                <div style="display:flex;flex-direction:column;gap:5px;">
                    ${eastDivs.map(row).join('')}
                </div>
            </div>
            <div>
                <div style="font-size:0.6rem;color:var(--accent-purple);text-transform:uppercase;letter-spacing:1px;font-family:var(--font-display);margin-bottom:0.25rem;padding-left:4px;">Western</div>
                <div style="display:flex;flex-direction:column;gap:5px;">
                    ${westDivs.map(row).join('')}
                </div>
            </div>
        </div>`;
}

// ── DRAG-SCROLL UTILITY ──────────────────────────
function enableDragScroll(el) {
    let isDown = false, startX, scrollLeft;
    el.style.cursor = 'grab';
    el.addEventListener('mousedown', e => {
        if (e.target.closest('a')) { /* allow links */ }
        isDown = true; el.style.cursor = 'grabbing';
        startX = e.pageX - el.offsetLeft;
        scrollLeft = el.scrollLeft;
        e.preventDefault();
    });
    el.addEventListener('mouseleave', () => { isDown = false; el.style.cursor = 'grab'; });
    el.addEventListener('mouseup', () => { isDown = false; el.style.cursor = 'grab'; });
    el.addEventListener('mousemove', e => {
        if (!isDown) return;
        const x = e.pageX - el.offsetLeft;
        el.scrollLeft = scrollLeft - (x - startX) * 1.5;
    });
}
</script>