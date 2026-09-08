% rebase('base.tpl', title='Team Profile', page='teams')

<div class="page-container">
    <!-- Profile header -->
    <div class="profile-header" id="teamHeader">
        <div class="skeleton" style="width:120px;height:120px;border-radius:50%;"></div>
        <div style="flex:1;">
            <div class="skeleton skeleton-title"></div>
            <div class="skeleton skeleton-text" style="width:40%;"></div>
        </div>
    </div>

    <!-- Season selector -->
    <div class="d-flex align-items-center gap-3 mb-4">
        <label class="form-label mb-0">Season</label>
        <select id="seasonSel" class="form-select" style="width:auto;"></select>
    </div>

    <!-- Tabs -->
    <div class="nav-tabs-nba" id="teamTabs">
        <button class="tab-btn active" data-tab="overview">Overview</button>
        <button class="tab-btn" data-tab="roster">Roster</button>
        <button class="tab-btn" data-tab="games">Games</button>
        <button class="tab-btn" data-tab="charts">Charts</button>
        <button class="tab-btn" data-tab="h2h">Head to Head</button>
        <button class="tab-btn" data-tab="streaks">Streaks</button>
        <button class="tab-btn" data-tab="salaries">Salaries</button>
    </div>

    <!-- Tab content -->
    <div id="tabContent"></div>
</div>

<script>
function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
const TEAM_ID = window.location.pathname.split('/').filter(Boolean).pop();
let teamInfo = null;
let currentSeason = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Load team info
    teamInfo = await NBA.fetchJSON(`/team/api/${TEAM_ID}`);
    if (!teamInfo) { NBA.showError(document.getElementById('teamHeader'), 'Team not found'); return; }

    // Render header
    const hdr = document.getElementById('teamHeader');
    hdr.innerHTML = `
        <img class="profile-img" src="/static/images/logos/${teamInfo.abbreviation}.png" alt="${teamInfo.abbreviation}"
             onerror="this.onerror=null;this.src='/static/images/player-placeholder.svg';">
        <div class="profile-info">
            <h1>${teamInfo.full_name}</h1>
            <div class="profile-meta">
                <span class="badge-conference">${teamInfo.conference || ''}</span>
                <span class="badge-position">${teamInfo.division || ''}</span>
                <span style="color:var(--text-secondary);font-size:0.85rem;">${teamInfo.city || ''}</span>
                <span style="color:var(--text-muted);font-size:0.85rem;">Est. ${teamInfo.year_founded || 'N/A'}</span>
            </div>
        </div>`;

    // Load seasons
    const seasons = await NBA.fetchJSON(`/team/api/${TEAM_ID}/seasons`);
    const sel = document.getElementById('seasonSel');
    if (seasons && seasons.length) {
        seasons.forEach((s, i) => {
            const opt = document.createElement('option');
            opt.value = s.season; opt.text = seasonLabel(s.season);
            if (i === 0) opt.selected = true;
            sel.appendChild(opt);
        });
        currentSeason = seasons[0].season;
    }

    sel.addEventListener('change', () => {
        currentSeason = parseInt(sel.value);
        loadActiveTab();
    });

    // Tabs
    document.querySelectorAll('#teamTabs .tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#teamTabs .tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadActiveTab();
        });
    });

    loadActiveTab();
});

function getActiveTab() {
    return document.querySelector('#teamTabs .tab-btn.active')?.dataset.tab || 'overview';
}

async function loadActiveTab() {
    const tab = getActiveTab();
    const el = document.getElementById('tabContent');
    NBA.showLoading(el);

    if (tab === 'overview') await loadOverview(el);
    else if (tab === 'roster') await loadRoster(el);
    else if (tab === 'games') await loadGames(el);
    else if (tab === 'charts') await loadCharts(el);
    else if (tab === 'h2h') await loadH2H(el);
    else if (tab === 'streaks') await loadStreaks(el);
    else if (tab === 'salaries') await loadSalaries(el);
}

async function loadOverview(el) {
    const [seasons, leaders] = await Promise.all([
        NBA.fetchJSON(`/team/api/${TEAM_ID}/seasons`),
        NBA.fetchJSON(`/team/api/${TEAM_ID}/leaders?season=${currentSeason}`)
    ]);
    if (!seasons) { NBA.showError(el); return; }
    const s = seasons.find(x => x.season == currentSeason) || seasons[0];
    if (!s) { el.innerHTML = '<p class="text-muted">No season data.</p>'; return; }

    // Compute division rank from standings data
    const divRank = s.conf_rank || '-';

    el.innerHTML = `
        <div class="stats-grid mb-4">
            <div class="stat-card"><div class="stat-value">${s.wins || 0}-${s.losses || 0}</div><div class="stat-label">Record</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(s.ppg)}</div><div class="stat-label">PPG</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(s.rpg)}</div><div class="stat-label">RPG</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(s.apg)}</div><div class="stat-label">APG</div></div>
            <div class="stat-card"><div class="stat-value">${s.fg_pct ? (s.fg_pct*100).toFixed(1)+'%' : '-'}</div><div class="stat-label">FG%</div></div>
            <div class="stat-card"><div class="stat-value">${s.fg3_pct ? (s.fg3_pct*100).toFixed(1)+'%' : '-'}</div><div class="stat-label">3PT%</div></div>
            <div class="stat-card"><div class="stat-value">${divRank}</div><div class="stat-label">Conf Rank</div></div>
            <div class="stat-card"><div class="stat-value">${teamInfo.division || '-'}</div><div class="stat-label">Division</div></div>
        </div>

        <!-- Team Leaders -->
        ${leaders ? `
        <div class="section-header" style="margin-bottom:1rem;">
            <h2 style="font-size:1rem;"><span class="section-icon"></span>Team Leaders &mdash; ${seasonLabel(currentSeason)}</h2>
        </div>
        <div class="row g-4 mb-4">
            <div class="col-md-4">
                <div class="card h-100"><div class="card-header"><h5 style="margin:0;font-size:0.85rem;"><i class="bi bi-trophy me-2" style="color:var(--accent-cyan);"></i>Scoring</h5></div>
                <div class="card-body" style="padding:0.5rem;">${renderMiniLeader(leaders.scorers, 'ppg', 'PPG')}</div></div>
            </div>
            <div class="col-md-4">
                <div class="card h-100"><div class="card-header"><h5 style="margin:0;font-size:0.85rem;"><i class="bi bi-arrow-repeat me-2" style="color:var(--accent-purple);"></i>Rebounds</h5></div>
                <div class="card-body" style="padding:0.5rem;">${renderMiniLeader(leaders.rebounders, 'rpg', 'RPG')}</div></div>
            </div>
            <div class="col-md-4">
                <div class="card h-100"><div class="card-header"><h5 style="margin:0;font-size:0.85rem;"><i class="bi bi-hand-index me-2" style="color:var(--accent-blue);"></i>Assists</h5></div>
                <div class="card-body" style="padding:0.5rem;">${renderMiniLeader(leaders.assisters, 'apg', 'APG')}</div></div>
            </div>
        </div>` : ''}

        <!-- Season Charts -->
        <div class="row g-4">
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartOverviewPts" height="260"></canvas></div></div>
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartOverviewRecord" height="260"></canvas></div></div>
        </div>`;

    // Draw overview charts using season history
    if (seasons.length > 1) {
        const rev = [...seasons].reverse();
        const lbl = rev.map(x => seasonLabel(x.season));
        const ctx1 = document.getElementById('chartOverviewPts').getContext('2d');
        new Chart(ctx1, {
            type:'bar', data:{ labels:lbl, datasets:[{ label:'PPG', data:rev.map(x=>x.ppg), backgroundColor:NBA.CYAN+'80', borderColor:NBA.CYAN, borderWidth:1, borderRadius:4 }] },
            options:{ responsive:true, plugins:{ legend:{display:false}, title:{display:true,text:'Points Per Game by Season',color:'#e8e8f0'} }, scales:{ y:{grid:{color:'rgba(42,42,68,0.3)'},beginAtZero:false}, x:{grid:{display:false}} } }
        });
        const ctx2 = document.getElementById('chartOverviewRecord').getContext('2d');
        new Chart(ctx2, {
            type:'bar', data:{ labels:lbl, datasets:[
                { label:'Wins', data:rev.map(x=>x.wins), backgroundColor:NBA.GREEN+'80', borderColor:NBA.GREEN, borderWidth:1, borderRadius:4 },
                { label:'Losses', data:rev.map(x=>x.losses), backgroundColor:NBA.RED+'80', borderColor:NBA.RED, borderWidth:1, borderRadius:4 }
            ] },
            options:{ responsive:true, plugins:{ legend:{labels:{color:'#e8e8f0'}}, title:{display:true,text:'Wins / Losses by Season',color:'#e8e8f0'} }, scales:{ y:{grid:{color:'rgba(42,42,68,0.3)'},beginAtZero:true, stacked:true}, x:{grid:{display:false}, stacked:true} } }
        });
    }
}

function renderMiniLeader(list, key, label) {
    if (!list || !list.length) return '<p style="color:var(--text-muted);font-size:0.8rem;">No data</p>';
    return list.map((p, i) => `
        <a href="/player/${p.player_id}" class="standings-row" style="text-decoration:none;color:inherit;padding:6px 8px;">
            <span class="rank-num" style="font-size:0.75rem;min-width:20px;">${i+1}</span>
            <img src="https://cdn.nba.com/headshots/nba/latest/260x190/${p.player_id}.png"
                 style="width:28px;height:28px;border-radius:50%;object-fit:cover;margin-right:6px;" onerror="this.onerror=null;this.src='/static/images/player-placeholder.svg';">
            <span style="flex:1;font-size:0.8rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.full_name}</span>
            <span class="num" style="font-weight:700;color:var(--accent-cyan);">${NBA.fmt(p[key])}</span>
            <span style="color:var(--text-muted);font-size:0.6rem;margin-left:2px;">${label}</span>
        </a>`
    ).join('');
}

async function loadRoster(el) {
    const roster = await NBA.fetchJSON(`/team/api/${TEAM_ID}/roster?season=${currentSeason}`);
    if (!roster || !roster.length) { el.innerHTML = '<p style="color:var(--text-muted);">No roster data.</p>'; return; }

    el.innerHTML = `<div class="roster-grid">
        ${roster.map(p => `
            <a href="/player/${p.player_id}" class="featured-card animate-in" style="text-decoration:none;color:inherit;display:flex;align-items:center;gap:12px;">
                <div style="width:48px;height:48px;border-radius:50%;background:var(--bg-secondary);overflow:hidden;flex-shrink:0;border:2px solid var(--border-color);">
                    <img src="https://cdn.nba.com/headshots/nba/latest/260x190/${p.player_id}.png"
                         style="width:100%;height:100%;object-fit:cover;"
                         onerror="this.onerror=null;this.src='/static/images/player-placeholder.svg';">
                </div>
                <div>
                    <div style="font-family:var(--font-display);font-size:0.95rem;">${p.full_name}</div>
                    <div style="display:flex;gap:6px;margin-top:4px;">
                        <span class="badge-position">${p.position || '?'}</span>
                        ${p.jersey_number ? `<span style="color:var(--text-muted);font-size:0.75rem;">#${p.jersey_number}</span>` : ''}
                    </div>
                </div>
            </a>
        `).join('')}
    </div>`;
}

async function loadGames(el) {
    const games = await NBA.fetchJSON(`/team/api/${TEAM_ID}/games?season=${currentSeason}`);
    if (!games || !games.length) { el.innerHTML = '<p style="color:var(--text-muted);">No game data.</p>'; return; }

    el.innerHTML = `
        <div style="overflow-x:auto;">
            <table class="table-dark-custom">
                <thead><tr>
                    <th>Date</th><th>Opponent</th><th>Result</th><th>Score</th><th>PTS</th><th>REB</th><th>AST</th>
                </tr></thead>
                <tbody>
                    ${games.map(g => `<tr>
                        <td class="num">${g.game_date || ''}</td>
                        <td>${g.matchup || ''}</td>
                        <td><span class="${g.wl === 'W' ? 'badge-win' : 'badge-loss'}">${g.wl || ''}</span></td>
                        <td class="num">${g.pts || ''}-${g.opp_pts || ''}</td>
                        <td class="num">${g.pts || ''}</td>
                        <td class="num">${g.reb || ''}</td>
                        <td class="num">${g.ast || ''}</td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>`;
}

async function loadCharts(el) {
    const [seasons, games] = await Promise.all([
        NBA.fetchJSON(`/team/api/${TEAM_ID}/seasons`),
        NBA.fetchJSON(`/team/api/${TEAM_ID}/games?season=${currentSeason}`)
    ]);
    if (!seasons || !seasons.length) { NBA.showError(el); return; }

    // Current season stat for comparison
    const cur = seasons.find(x => x.season == currentSeason) || seasons[0];

    el.innerHTML = `
        <!-- Per-Season Stats Comparison card -->
        <div class="card mb-4">
            <div class="card-header"><h5 style="margin:0;font-size:0.9rem;"><i class="bi bi-bar-chart-steps me-2" style="color:var(--accent-cyan);"></i>Season-by-Season Comparison</h5></div>
            <div class="card-body" style="overflow-x:auto;">
                <table class="table-dark-custom" style="font-size:0.8rem;">
                    <thead><tr><th>Season</th><th>W</th><th>L</th><th>Win%</th><th>PPG</th><th>RPG</th><th>APG</th><th>FG%</th><th>3PT%</th><th>FT%</th><th>ORtg</th><th>DRtg</th><th>NRtg</th></tr></thead>
                    <tbody>${seasons.map(s => {
                        const isCur = s.season == currentSeason;
                        const hl = isCur ? 'background:rgba(0,240,255,0.08);font-weight:600;' : '';
                        return `<tr style="${hl}">
                            <td class="num">${seasonLabel(s.season)}</td>
                            <td class="num">${s.wins||0}</td><td class="num">${s.losses||0}</td>
                            <td class="num">${s.win_pct ? (s.win_pct*100).toFixed(1)+'%' : '-'}</td>
                            <td class="num">${NBA.fmt(s.ppg)}</td>
                            <td class="num">${NBA.fmt(s.rpg)}</td>
                            <td class="num">${NBA.fmt(s.apg)}</td>
                            <td class="num">${s.fg_pct?(s.fg_pct*100).toFixed(1)+'%':'-'}</td>
                            <td class="num">${s.fg3_pct?(s.fg3_pct*100).toFixed(1)+'%':'-'}</td>
                            <td class="num">${s.ft_pct?(s.ft_pct*100).toFixed(1)+'%':'-'}</td>
                            <td class="num">${s.off_rating?NBA.fmt(s.off_rating):'-'}</td>
                            <td class="num">${s.def_rating?NBA.fmt(s.def_rating):'-'}</td>
                            <td class="num">${s.net_rating?NBA.fmt(s.net_rating):'-'}</td>
                        </tr>`;}).join('')}</tbody>
                </table>
            </div>
        </div>

        <!-- Season History Charts -->
        <div class="row g-4 mb-4">
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartWins" height="280"></canvas></div></div>
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartPPG" height="280"></canvas></div></div>
        </div>
        <div class="row g-4 mb-4">
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartFgPct" height="280"></canvas></div></div>
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartRatings" height="280"></canvas></div></div>
        </div>

        <!-- Current Season Game-by-Game chart -->
        ${games && games.length ? '<div class="chart-container mb-4"><canvas id="chartGamePts" height="280"></canvas></div>' : ''}`;

    const rev = [...seasons].reverse();
    const labels = rev.map(s => seasonLabel(s.season));

    // Wins chart
    const ctx1 = document.getElementById('chartWins').getContext('2d');
    new Chart(ctx1, {
        type:'bar', data:{ labels, datasets:[
            { label:'Wins', data:rev.map(s=>s.wins), backgroundColor:NBA.GREEN+'80', borderColor:NBA.GREEN, borderWidth:1, borderRadius:4 },
            { label:'Losses', data:rev.map(s=>s.losses), backgroundColor:NBA.RED+'80', borderColor:NBA.RED, borderWidth:1, borderRadius:4 }
        ]},
        options:{ responsive:true, plugins:{ legend:{labels:{color:'#e8e8f0'}}, title:{display:true,text:'Wins / Losses',color:'#e8e8f0'} }, scales:{ y:{grid:{color:'rgba(42,42,68,0.3)'},beginAtZero:true,stacked:true}, x:{grid:{display:false},stacked:true} } }
    });

    // PPG chart
    const ctx2 = document.getElementById('chartPPG').getContext('2d');
    new Chart(ctx2, {
        type:'line', data:{ labels, datasets:[{label:'PPG', data:rev.map(s=>s.ppg), borderColor:NBA.PURPLE, backgroundColor:NBA.createGradient(ctx2,NBA.PURPLE), fill:true, tension:0.4, pointRadius:3}] },
        options:{ responsive:true, plugins:{legend:{display:false},title:{display:true,text:'Points Per Game',color:'#e8e8f0'}}, scales:{y:{grid:{color:'rgba(42,42,68,0.3)'}},x:{grid:{display:false}}} }
    });

    // FG% / 3PT% chart
    const ctx3 = document.getElementById('chartFgPct').getContext('2d');
    new Chart(ctx3, {
        type:'line', data:{ labels, datasets:[
            { label:'FG%', data:rev.map(s=>s.fg_pct?(s.fg_pct*100).toFixed(1):null), borderColor:NBA.CYAN, tension:0.4, pointRadius:3 },
            { label:'3PT%', data:rev.map(s=>s.fg3_pct?(s.fg3_pct*100).toFixed(1):null), borderColor:NBA.ORANGE, tension:0.4, pointRadius:3 }
        ]},
        options:{ responsive:true, plugins:{legend:{labels:{color:'#e8e8f0'}},title:{display:true,text:'Shooting Percentages',color:'#e8e8f0'}}, scales:{y:{grid:{color:'rgba(42,42,68,0.3)'},ticks:{callback:v=>v+'%'}},x:{grid:{display:false}}} }
    });

    // Off/Def Rating chart
    const ctx4 = document.getElementById('chartRatings').getContext('2d');
    new Chart(ctx4, {
        type:'line', data:{ labels, datasets:[
            { label:'Off Rating', data:rev.map(s=>s.off_rating), borderColor:NBA.GREEN, tension:0.4, pointRadius:3 },
            { label:'Def Rating', data:rev.map(s=>s.def_rating), borderColor:NBA.RED, tension:0.4, pointRadius:3 }
        ]},
        options:{ responsive:true, plugins:{legend:{labels:{color:'#e8e8f0'}},title:{display:true,text:'Offensive / Defensive Rating',color:'#e8e8f0'}}, scales:{y:{grid:{color:'rgba(42,42,68,0.3)'}},x:{grid:{display:false}}} }
    });

    // Game-by-game points for current season
    if (games && games.length) {
        const gLabels = games.map((g,i) => 'G'+(games.length - i)).reverse();
        const gPts = [...games].reverse().map(g => g.pts);
        const gColors = [...games].reverse().map(g => g.wl==='W' ? NBA.GREEN+'80' : NBA.RED+'80');
        const ctx5 = document.getElementById('chartGamePts').getContext('2d');
        new Chart(ctx5, {
            type:'bar', data:{ labels:gLabels, datasets:[{label:'Points', data:gPts, backgroundColor:gColors, borderWidth:0, borderRadius:2}] },
            options:{ responsive:true, plugins:{legend:{display:false},title:{display:true,text:`Points per Game — ${seasonLabel(currentSeason)}`,color:'#e8e8f0'},tooltip:{callbacks:{label:(c)=>`${c.raw} pts`}}}, scales:{y:{grid:{color:'rgba(42,42,68,0.3)'},beginAtZero:true},x:{grid:{display:false},ticks:{maxTicksLimit:20}}} }
        });
    }
}

async function loadH2H(el) {
    el.innerHTML = `
        <div class="d-flex align-items-center gap-3 mb-3">
            <label class="form-label mb-0">Opponent</label>
            <select id="h2hOpponent" class="form-select" style="width:auto;"></select>
            <button class="btn-nba btn-nba-sm" onclick="fetchH2H()">Compare</button>
        </div>
        <div id="h2hResults"></div>`;

    const teams = await NBA.fetchJSON('/team/api/all');
    if (!teams) return;
    const sel = document.getElementById('h2hOpponent');
    teams.filter(t => t.team_id != TEAM_ID).forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.team_id;
        opt.text = t.full_name;
        sel.appendChild(opt);
    });
}

async function fetchH2H() {
    const opp = document.getElementById('h2hOpponent').value;
    const res = document.getElementById('h2hResults');
    NBA.showLoading(res);
    const data = await NBA.fetchJSON(`/team/api/${TEAM_ID}/h2h?opponent_id=${opp}`);
    if (!data) { NBA.showError(res); return; }

    res.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-value">${data.total_games || 0}</div><div class="stat-label">Games</div></div>
            <div class="stat-card"><div class="stat-value" style="color:var(--accent-green);">${data.wins || 0}</div><div class="stat-label">Wins</div></div>
            <div class="stat-card"><div class="stat-value" style="color:var(--accent-red);">${data.losses || 0}</div><div class="stat-label">Losses</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(data.avg_pts)}</div><div class="stat-label">Avg Pts</div></div>
        </div>`;
}

async function loadSalaries(el) {
    const data = await NBA.fetchJSON(`/team/api/${TEAM_ID}/salaries?season=${currentSeason}`);
    const history = await NBA.fetchJSON(`/team/api/${TEAM_ID}/salaries/history`);
    if (!data || !data.players || !data.players.length) {
        el.innerHTML = '<p style="color:var(--text-muted);">No salary data for this season.</p>';
        return;
    }

    el.innerHTML = `
        <div class="stats-grid mb-4">
            <div class="stat-card"><div class="stat-value" style="color:var(--accent-green);">$${(data.total_payroll/1e6).toFixed(1)}M</div><div class="stat-label">Total Payroll</div></div>
            <div class="stat-card"><div class="stat-value">${data.players.length}</div><div class="stat-label">Players</div></div>
            <div class="stat-card"><div class="stat-value">$${(data.total_payroll / data.players.length / 1e6).toFixed(1)}M</div><div class="stat-label">Avg Salary</div></div>
            <div class="stat-card"><div class="stat-value">$${(data.players[0].salary/1e6).toFixed(1)}M</div><div class="stat-label">Highest</div></div>
        </div>
        ${history && history.length ? `<div class="chart-container mb-4"><canvas id="chartPayroll" height="280"></canvas></div>` : ''}
        <div style="overflow-x:auto;">
            <table class="table-dark-custom">
                <thead><tr><th>#</th><th>Player</th><th>Position</th><th>Salary</th><th>% of Cap</th></tr></thead>
                <tbody>${data.players.map((p, i) => `<tr style="cursor:pointer;" onclick="location.href='/player/${p.player_id}'">
                    <td class="num">${i + 1}</td>
                    <td><strong>${p.full_name}</strong></td>
                    <td>${p.position || '-'}</td>
                    <td class="num">$${(p.salary||0).toLocaleString('en-US')}</td>
                    <td class="num">${(p.salary / data.total_payroll * 100).toFixed(1)}%</td>
                </tr>`).join('')}</tbody>
            </table>
        </div>`;

    // Payroll history chart
    if (history && history.length) {
        const ctx = document.getElementById('chartPayroll').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: history.map(h => seasonLabel(h.season)),
                datasets: [{
                    label: 'Total Payroll',
                    data: history.map(h => h.total_payroll),
                    backgroundColor: NBA.createGradient(ctx, NBA.GOLD),
                    borderColor: NBA.GOLD,
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Payroll History', color: '#e8e8f0' },
                    tooltip: { callbacks: { label: (c) => '$' + (c.raw/1e6).toFixed(1) + 'M' } }
                },
                scales: {
                    y: { grid: { color: 'rgba(42,42,68,0.3)' }, ticks: { callback: v => '$'+(v/1e6).toFixed(0)+'M' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}

async function loadStreaks(el) {
    const data = await NBA.fetchJSON(`/team/api/${TEAM_ID}/streaks?season=${currentSeason}`);
    if (!data) { NBA.showError(el); return; }

    el.innerHTML = `
        <div class="stats-grid mb-4">
            <div class="stat-card"><div class="stat-value" style="color:var(--accent-green);">${data.longest_win_streak || 0}</div><div class="stat-label">Best Win Streak</div></div>
            <div class="stat-card"><div class="stat-value" style="color:var(--accent-red);">${data.longest_loss_streak || 0}</div><div class="stat-label">Worst Loss Streak</div></div>
            <div class="stat-card"><div class="stat-value">${data.current_streak || '-'}</div><div class="stat-label">Current Streak</div></div>
        </div>
        ${data.streaks && data.streaks.length ? `
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;">
            ${[...data.streaks].reverse().map(g => {
                const isWin = g.wl === 'W';
                const borderClr = isWin ? 'var(--accent-green)' : 'var(--accent-red)';
                const bgClr = isWin ? 'rgba(0,230,118,0.08)' : 'rgba(255,45,85,0.08)';
                return `<a href="/team/${g.opponent_id}" class="card" style="text-decoration:none;border-color:${borderClr};background:${bgClr};padding:10px 12px;">
                    <div style="display:flex;align-items:center;gap:8px;">
                        <img src="/static/images/logos/${g.opp_abbr}.png" style="width:28px;height:28px;"
                             onerror="this.onerror=null;this.src='/static/images/player-placeholder.svg';">
                        <div style="flex:1;min-width:0;">
                            <div style="font-family:var(--font-display);font-size:0.8rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                                vs ${g.opp_abbr || '???'}
                            </div>
                            <div style="font-size:0.65rem;color:var(--text-muted);">${g.game_date || ''}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:var(--font-mono);font-size:0.9rem;font-weight:700;color:${isWin ? 'var(--accent-green)' : 'var(--accent-red)'};">
                                ${g.pts || 0}-${g.opp_pts || 0}
                            </div>
                            <div style="font-size:0.6rem;font-weight:700;color:${isWin ? 'var(--accent-green)' : 'var(--accent-red)'};">${g.wl}</div>
                        </div>
                    </div>
                </a>`;
            }).join('')}
        </div>` : ''}`;
}
</script>
