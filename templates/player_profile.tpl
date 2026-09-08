% rebase('base.tpl', title='Player Profile', page='players')

<div class="page-container">
    <!-- Profile header -->
    <div class="profile-header" id="playerHeader">
        <div class="skeleton" style="width:120px;height:120px;border-radius:50%;"></div>
        <div style="flex:1;"><div class="skeleton skeleton-title"></div><div class="skeleton skeleton-text" style="width:50%;"></div></div>
    </div>

    <!-- Tabs -->
    <div class="nav-tabs-nba">
        <button class="tab-btn active" data-tab="career">Career Stats</button>
        <button class="tab-btn" data-tab="seasons">Season by Season</button>
        <button class="tab-btn" data-tab="games">Game Log</button>
        <button class="tab-btn" data-tab="awards">Awards</button>
        <button class="tab-btn" data-tab="similar">Similar Players</button>
        <button class="tab-btn" data-tab="salary">Salary</button>
    </div>

    <div id="tabContent"></div>
</div>

<script>
const PID = window.location.pathname.split('/').filter(Boolean).pop();
let playerInfo = null;

function seasonLabel(y) {
    if (!y) return '-';
    const next = (y % 100) + 1;
    return y + '/' + String(next).padStart(2, '0');
}

function teamLink(abbr, teamId) {
    if (!abbr) return '-';
    if (teamId) return `<a href="/team/${teamId}" style="color:var(--accent-cyan);text-decoration:none;">${abbr}</a>`;
    return abbr;
}

document.addEventListener('DOMContentLoaded', async () => {
    playerInfo = await NBA.fetchJSON(`/player/api/${PID}`);
    if (!playerInfo) { NBA.showError(document.getElementById('playerHeader'), 'Player not found'); return; }

    // Header
    const hdr = document.getElementById('playerHeader');
    const imgUrl = `https://cdn.nba.com/headshots/nba/latest/260x190/${PID}.png`;
    const teamBadge = playerInfo.team_abbreviation
        ? `<a href="/team/${playerInfo.team_id}" style="color:var(--accent-cyan);text-decoration:none;font-size:0.95rem;font-weight:600;"><i class="bi bi-people-fill me-1"></i>${playerInfo.team_name || playerInfo.team_abbreviation}</a>`
        : '';
    hdr.innerHTML = `
        <img class="profile-img" src="${imgUrl}" alt="${playerInfo.full_name}"
             onerror="this.src='https://cdn.nba.com/headshots/nba/latest/260x190/fallback.png'">
        <div class="profile-info">
            <h1>${playerInfo.full_name}</h1>
            ${teamBadge ? `<div style="margin-bottom:0.3rem;">${teamBadge}</div>` : ''}
            <div class="profile-meta">
                ${playerInfo.position ? `<span class="badge-position">${playerInfo.position}</span>` : ''}
                ${playerInfo.height ? `<span style="color:var(--text-secondary);font-size:0.85rem;">${playerInfo.height}</span>` : ''}
                ${playerInfo.weight ? `<span style="color:var(--text-secondary);font-size:0.85rem;">${playerInfo.weight} lbs</span>` : ''}
                ${playerInfo.country ? `<span style="color:var(--text-muted);font-size:0.85rem;"><i class="bi bi-geo-alt me-1"></i>${playerInfo.country}</span>` : ''}
                ${playerInfo.draft_year ? `<span style="color:var(--text-muted);font-size:0.85rem;">Draft: ${playerInfo.draft_year} #${playerInfo.draft_number || '?'}</span>` : ''}
            </div>
        </div>`;

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadTab();
        });
    });

    loadTab();
});

function activeTab() { return document.querySelector('.tab-btn.active')?.dataset.tab || 'career'; }

async function loadTab() {
    const tab = activeTab();
    const el = document.getElementById('tabContent');
    NBA.showLoading(el);

    if (tab === 'career') await loadCareer(el);
    else if (tab === 'seasons') await loadSeasons(el);
    else if (tab === 'games') await loadGames(el);
    else if (tab === 'awards') await loadAwards(el);
    else if (tab === 'similar') await loadSimilar(el);
    else if (tab === 'salary') await loadSalary(el);
}

async function loadCareer(el) {
    const data = await NBA.fetchJSON(`/player/api/${PID}/career`);
    if (!data) { NBA.showError(el); return; }

    const c = data.career_averages || {};
    const ss = data.seasons || [];
    // data arrives DESC (newest first) — charts need chronological ASC
    const ssChart = [...ss].reverse();

    el.innerHTML = `
        <div class="stats-grid mb-4">
            <div class="stat-card"><div class="stat-value">${NBA.fmt(c.ppg)}</div><div class="stat-label">PPG</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(c.rpg)}</div><div class="stat-label">RPG</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(c.apg)}</div><div class="stat-label">APG</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(c.spg)}</div><div class="stat-label">SPG</div></div>
            <div class="stat-card"><div class="stat-value">${NBA.fmt(c.bpg)}</div><div class="stat-label">BPG</div></div>
            <div class="stat-card"><div class="stat-value">${c.ts_pct ? (c.ts_pct*100).toFixed(1)+'%' : '-'}</div><div class="stat-label">TS%</div></div>
            <!--<div class="stat-card"><div class="stat-value">${c.game_score ? NBA.fmt(c.game_score) : '-'}</div><div class="stat-label">GameScore</div></div>-->
            <div class="stat-card"><div class="stat-value" style="color:${c.per ? (c.per >= 25 ? 'var(--accent-cyan)' : c.per >= 20 ? 'var(--accent-blue)' : c.per >= 15 ? 'var(--accent-purple)' : 'var(--accent-orange)') : 'var(--text-primary)'};">${c.per ? NBA.fmt(c.per, 2) : '-'}</div><div class="stat-label">PER</div></div>
            <div class="stat-card"><div class="stat-value">${ss.length}</div><div class="stat-label">Seasons</div></div>
        </div>

        ${ss.length ? `
        <div class="row g-4">
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartCareerPts" height="280"></canvas></div></div>
            <div class="col-lg-6"><div class="chart-container"><canvas id="chartCareerEff" height="280"></canvas></div></div>
        </div>` : ''}`;

    if (ssChart.length) {
        const labels = ssChart.map(s => seasonLabel(s.season));
        const pts = ssChart.map(s => s.ppg);
        const gs = ssChart.map(s => s.game_score);

        const ctx1 = document.getElementById('chartCareerPts').getContext('2d');
        new Chart(ctx1, {
            type: 'bar', data: { labels, datasets: [{ label: 'PPG', data: pts, backgroundColor: NBA.CYAN+'80', borderColor: NBA.CYAN, borderWidth: 1, borderRadius: 4 }] },
            options: { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: 'Points Per Game', color: '#e8e8f0' } }, scales: { y: { grid: { color: 'rgba(42,42,68,0.3)' }, beginAtZero: true }, x: { grid: { display: false } } } }
        });

        const ctx2 = document.getElementById('chartCareerEff').getContext('2d');
        new Chart(ctx2, {
            type: 'line', data: { labels, datasets: [{ label: 'GameScore', data: gs, borderColor: NBA.GREEN, backgroundColor: NBA.createGradient(ctx2, NBA.GREEN), fill: true, tension: 0.4, pointRadius: 3 }] },
            options: { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: 'GameScore', color: '#e8e8f0' } }, scales: { y: { grid: { color: 'rgba(42,42,68,0.3)' } }, x: { grid: { display: false } } } }
        });
    }
}

async function loadSeasons(el) {
    const data = await NBA.fetchJSON(`/player/api/${PID}/career`);
    if (!data || !data.seasons) { NBA.showError(el); return; }

    el.innerHTML = `
        <div style="overflow-x:auto;">
            <table class="table-dark-custom">
                <thead><tr>
                    <th>Season</th><th>Team</th><th>GP</th><th>PPG</th><th>RPG</th><th>APG</th><th>SPG</th><th>BPG</th><th>FG%</th><th>3P%</th><th>FT%</th><th>TS%</th><th>GmSc</th><th>PER</th>
                </tr></thead>
                <tbody>
                    ${data.seasons.map(s => `<tr>
                        <td class="num">${seasonLabel(s.season)}</td>
                        <td>${teamLink(s.team_abbreviation, s.team_id)}</td>
                        <td class="num">${s.gp || 0}</td>
                        <td class="num">${NBA.fmt(s.ppg)}</td>
                        <td class="num">${NBA.fmt(s.rpg)}</td>
                        <td class="num">${NBA.fmt(s.apg)}</td>
                        <td class="num">${NBA.fmt(s.spg)}</td>
                        <td class="num">${NBA.fmt(s.bpg)}</td>
                        <td class="num">${s.fg_pct ? (s.fg_pct*100).toFixed(1) : '-'}</td>
                        <td class="num">${s.fg3_pct ? (s.fg3_pct*100).toFixed(1) : '-'}</td>
                        <td class="num">${s.ft_pct ? (s.ft_pct*100).toFixed(1) : '-'}</td>
                        <td class="num">${s.ts_pct ? (s.ts_pct*100).toFixed(1) : '-'}</td>
                        <td class="num">${s.game_score ? NBA.fmt(s.game_score) : '-'}</td>
                        <td class="num" style="color:${s.per ? (s.per >= 25 ? 'var(--accent-cyan)' : s.per >= 20 ? 'var(--accent-blue)' : 'var(--text-primary)') : 'var(--text-muted)'};">${s.per ? NBA.fmt(s.per, 2) : '-'}</td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>`;
}

async function loadGames(el) {
    // Fetch career data to get available seasons
    const career = await NBA.fetchJSON(`/player/api/${PID}/career`);
    const seasons = career && career.seasons ? career.seasons.map(s => s.season) : [];
    if (!seasons.length) { el.innerHTML = '<p style="color:var(--text-muted);">No game data available.</p>'; return; }
    const latestSeason = seasons[0]; // seasons arrive DESC (newest first)

    el.innerHTML = `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
            <label style="color:var(--text-secondary);font-size:0.85rem;">Season:</label>
            <select id="gameSeasonSelect" class="form-select form-select-sm" style="width:auto;background:var(--bg-card);color:var(--text-primary);border:1px solid var(--border-color);">
                ${seasons.map(s => `<option value="${s}">${seasonLabel(s)}</option>`).join('')}
            </select>
        </div>
        <div id="gameLogBody"></div>`;

    const sel = document.getElementById('gameSeasonSelect');
    sel.addEventListener('change', () => renderGameLog(sel.value));
    renderGameLog(latestSeason);
}

async function renderGameLog(season) {
    const body = document.getElementById('gameLogBody');
    if (!body) return;
    body.innerHTML = '<div class="skeleton" style="height:200px;"></div>';
    const data = await NBA.fetchJSON(`/player/api/${PID}/games?season=${season}&limit=82`);
    if (!data || !data.length) { body.innerHTML = '<p style="color:var(--text-muted);">No game data for this season.</p>'; return; }

    body.innerHTML = `
        <div style="overflow-x:auto;">
            <table class="table-dark-custom">
                <thead><tr>
                    <th>Date</th><th>Matchup</th><th>W/L</th><th>MIN</th><th>PTS</th><th>REB</th><th>AST</th><th>STL</th><th>BLK</th><th>FG</th><th>3PT</th>
                </tr></thead>
                <tbody>
                    ${data.map(g => `<tr>
                        <td class="num">${g.game_date || ''}</td>
                        <td>${g.matchup || ''}</td>
                        <td><span class="${g.wl === 'W' ? 'badge-win' : 'badge-loss'}">${g.wl || ''}</span></td>
                        <td class="num">${g.min || ''}</td>
                        <td class="num"><strong>${g.pts || 0}</strong></td>
                        <td class="num">${g.reb || 0}</td>
                        <td class="num">${g.ast || 0}</td>
                        <td class="num">${g.stl || 0}</td>
                        <td class="num">${g.blk || 0}</td>
                        <td class="num">${g.fgm || 0}-${g.fga || 0}</td>
                        <td class="num">${g.fg3m || 0}-${g.fg3a || 0}</td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>`;
}

async function loadAwards(el) {
    const data = await NBA.fetchJSON(`/player/api/${PID}/awards`);
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No awards on record.</p>'; return; }

    el.innerHTML = `<div style="display:flex;gap:8px;flex-wrap:wrap;">
        ${data.map(a => `<div class="badge-award" style="padding:8px 16px;font-size:0.85rem;">
            <i class="bi bi-trophy me-1"></i>${a.description || a.award_type || 'Award'} ${a.season ? `(${seasonLabel(a.season)})` : ''}
        </div>`).join('')}
    </div>`;
}

async function loadSimilar(el) {
    const data = await NBA.fetchJSON(`/player/api/${PID}/similar`);
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">Not enough data for similarity.</p>'; return; }

    el.innerHTML = `
        <p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:1rem;">Players with similar career averages (Euclidean distance on PPG, RPG, APG, SPG, BPG)</p>
        <div class="roster-grid">
            ${data.map((p, i) => `
                <a href="/player/${p.player_id}" class="featured-card animate-in" style="text-decoration:none;color:inherit;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <div style="width:48px;height:48px;border-radius:50%;background:var(--bg-secondary);overflow:hidden;flex-shrink:0;border:2px solid var(--border-color);display:flex;align-items:center;justify-content:center;">
                            <img src="https://cdn.nba.com/headshots/nba/latest/260x190/${p.player_id}.png"
                                 style="width:100%;height:100%;object-fit:cover;"
                                 onerror="this.parentElement.innerHTML='<i class=\\'bi bi-person\\' style=\\'font-size:1.2rem;color:var(--text-muted);\\'></i>'">
                        </div>
                        <div style="flex:1;min-width:0;">
                            <div style="font-family:var(--font-display);font-size:0.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.full_name}</div>
                            <div style="color:var(--text-muted);font-size:0.75rem;">
                                ${NBA.fmt(p.ppg)} ppg &middot; ${NBA.fmt(p.rpg)} rpg &middot; ${NBA.fmt(p.apg)} apg
                            </div>
                            <div style="color:var(--accent-cyan);font-size:0.7rem;margin-top:2px;">Distance: ${NBA.fmt(p.distance, 2)}</div>
                        </div>
                        <span class="rank" style="font-size:1.2rem;">${i+1}</span>
                    </div>
                </a>
            `).join('')}
        </div>`;
}

async function loadSalary(el) {
    const data = await NBA.fetchJSON(`/player/api/${PID}/salary-history`);
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No salary data available.</p>'; return; }

    // data arrives sorted DESC (newest first) — table shows that order
    // chart needs chronological ASC
    const chartData = [...data].reverse();

    el.innerHTML = `<div class="chart-container"><canvas id="chartSalary" height="300"></canvas></div>
        <div style="overflow-x:auto;margin-top:1rem;">
            <table class="table-dark-custom">
                <thead><tr><th>Season</th><th>Team</th><th>Salary</th></tr></thead>
                <tbody>${data.map(s => `<tr><td class="num">${seasonLabel(s.season)}</td><td>${teamLink(s.abbreviation, s.team_id)}</td><td class="num">$${(s.salary||0).toLocaleString('en-US')}</td></tr>`).join('')}</tbody>
                <tfoot><tr style="border-top:2px solid var(--accent-cyan);font-weight:700;">
                    <td colspan="2">Career Total</td>
                    <td class="num" style="color:var(--accent-cyan);">$${data.reduce((sum,s) => sum + (s.salary||0), 0).toLocaleString('en-US')}</td>
                </tr></tfoot>
            </table>
        </div>`;

    const ctx = document.getElementById('chartSalary').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.map(s => s.abbreviation ? `${seasonLabel(s.season)} (${s.abbreviation})` : seasonLabel(s.season)),
            datasets: [{ label: 'Salary', data: chartData.map(s => s.salary), backgroundColor: NBA.GOLD+'80', borderColor: NBA.GOLD, borderWidth: 1, borderRadius: 4 }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false }, title: { display: true, text: 'Salary History', color: '#e8e8f0' } },
            scales: {
                y: { grid: { color: 'rgba(42,42,68,0.3)' }, ticks: { callback: v => '$'+(v/1e6).toFixed(1)+'M' } },
                x: { grid: { display: false } }
            }
        }
    });
}
</script>
