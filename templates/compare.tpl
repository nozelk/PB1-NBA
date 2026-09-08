% rebase('base.tpl', title='Compare', page='compare')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>Compare</h2>
    </div>

    <!-- Mode toggle -->
    <div class="pill-group mb-4">
        <button class="pill active" id="modePlayer" onclick="setMode('players')">Players</button>
        <button class="pill" id="modeTeam" onclick="setMode('teams')">Teams</button>
    </div>

    <!-- Player compare -->
    <div id="playerCompare">
        <div class="row g-3 mb-4">
            <div class="col-md-5">
                <label class="form-label">Player 1</label>
                <select id="p1" class="form-select"></select>
            </div>
            <div class="col-md-5">
                <label class="form-label">Player 2</label>
                <select id="p2" class="form-select"></select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button class="btn-nba w-100" onclick="comparePlayers()">Compare</button>
            </div>
        </div>
        <div id="playerResults"></div>
    </div>

    <!-- Team compare -->
    <div id="teamCompare" style="display:none;">
        <div class="row g-3 mb-4">
            <div class="col-md-4">
                <label class="form-label">Team 1</label>
                <select id="t1" class="form-select"></select>
            </div>
            <div class="col-md-4">
                <label class="form-label">Team 2</label>
                <select id="t2" class="form-select"></select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Season</label>
                <select id="compSeason" class="form-select"></select>
            </div>
            <div class="col-md-2 d-flex align-items-end">
                <button class="btn-nba w-100" onclick="compareTeams()">Compare</button>
            </div>
        </div>
        <div id="teamResults"></div>
    </div>
</div>

<script>
function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
document.addEventListener('DOMContentLoaded', async () => {
    // Load players
    const players = await NBA.fetchJSON('/player/api/all');
    if (players) {
        ['p1', 'p2'].forEach(id => {
            const sel = document.getElementById(id);
            players.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.player_id;
                opt.text = p.full_name;
                sel.appendChild(opt);
            });
        });
    }

    // Load teams
    const teams = await NBA.fetchJSON('/team/api/all');
    if (teams) {
        ['t1', 't2'].forEach(id => {
            const sel = document.getElementById(id);
            teams.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t.team_id;
                opt.text = t.full_name;
                sel.appendChild(opt);
            });
        });
    }

    // Seasons
    const seasons = await NBA.fetchJSON('/api/seasons');
    if (seasons) {
        const sel = document.getElementById('compSeason');
        seasons.forEach((s, i) => {
            const opt = document.createElement('option');
            opt.value = s; opt.text = seasonLabel(s);
            if (i === 0) opt.selected = true;
            sel.appendChild(opt);
        });
    }
});

function setMode(mode) {
    document.getElementById('playerCompare').style.display = mode === 'players' ? '' : 'none';
    document.getElementById('teamCompare').style.display = mode === 'teams' ? '' : 'none';
    document.getElementById('modePlayer').classList.toggle('active', mode === 'players');
    document.getElementById('modeTeam').classList.toggle('active', mode === 'teams');
}

async function comparePlayers() {
    const id1 = document.getElementById('p1').value;
    const id2 = document.getElementById('p2').value;
    const el = document.getElementById('playerResults');
    NBA.showLoading(el);

    const data = await NBA.fetchJSON(`/api/compare/players?id1=${id1}&id2=${id2}`);
    if (!data || !data.player1 || !data.player2) { NBA.showError(el); return; }

    const p1 = data.player1, p2 = data.player2;
    const cats = [
        { key: 'ppg', label: 'PPG' }, { key: 'rpg', label: 'RPG' }, { key: 'apg', label: 'APG' },
        { key: 'spg', label: 'SPG' }, { key: 'bpg', label: 'BPG' },
        { key: 'fg_pct', label: 'FG%', pct: true }, { key: 'fg3_pct', label: '3PT%', pct: true },
        { key: 'ts_pct', label: 'TS%', pct: true }, { key: 'game_score', label: 'GmSc' }
    ];

    el.innerHTML = `
        <div class="row g-4 mb-4">
            <div class="col-md-6 text-center">
                <h3 style="color:var(--accent-cyan);">${p1.full_name}</h3>
                <span class="badge-position">${p1.position || '-'}</span>
            </div>
            <div class="col-md-6 text-center">
                <h3 style="color:var(--accent-purple);">${p2.full_name}</h3>
                <span class="badge-position">${p2.position || '-'}</span>
            </div>
        </div>
        <div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>Stat</th><th style="text-align:right;">${p1.full_name}</th><th style="text-align:right;">${p2.full_name}</th></tr></thead>
            <tbody>${cats.map(c => {
                const v1 = c.pct ? (p1[c.key] ? (p1[c.key]*100).toFixed(1)+'%' : '-') : NBA.fmt(p1[c.key]);
                const v2 = c.pct ? (p2[c.key] ? (p2[c.key]*100).toFixed(1)+'%' : '-') : NBA.fmt(p2[c.key]);
                const raw1 = c.pct ? (p1[c.key]||0)*100 : (p1[c.key]||0);
                const raw2 = c.pct ? (p2[c.key]||0)*100 : (p2[c.key]||0);
                return `<tr>
                    <td>${c.label}</td>
                    <td class="num" style="text-align:right;color:${raw1 >= raw2 ? 'var(--accent-green)' : 'var(--text-primary)'};">${v1}</td>
                    <td class="num" style="text-align:right;color:${raw2 >= raw1 ? 'var(--accent-green)' : 'var(--text-primary)'};">${v2}</td>
                </tr>`;
            }).join('')}</tbody>
        </table></div>

        <div class="chart-container mt-4"><canvas id="radarCompare" height="350"></canvas></div>`;

    // Radar chart
    const ctx = document.getElementById('radarCompare').getContext('2d');
    const radarCats = ['ppg','rpg','apg','spg','bpg'];
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: radarCats.map(c => c.toUpperCase()),
            datasets: [
                { label: p1.full_name, data: radarCats.map(c => p1[c] || 0), borderColor: NBA.CYAN, backgroundColor: NBA.CYAN+'30', pointBackgroundColor: NBA.CYAN },
                { label: p2.full_name, data: radarCats.map(c => p2[c] || 0), borderColor: NBA.PURPLE, backgroundColor: NBA.PURPLE+'30', pointBackgroundColor: NBA.PURPLE }
            ]
        },
        options: {
            responsive: true,
            scales: { r: { grid: { color: 'rgba(42,42,68,0.5)' }, pointLabels: { color: '#e8e8f0', font: { family: "'Oswald', sans-serif" } }, ticks: { display: false }, beginAtZero: true } },
            plugins: { legend: { labels: { color: '#e8e8f0' } } }
        }
    });
}

async function compareTeams() {
    const id1 = document.getElementById('t1').value;
    const id2 = document.getElementById('t2').value;
    const season = document.getElementById('compSeason').value;
    const el = document.getElementById('teamResults');
    NBA.showLoading(el);

    const data = await NBA.fetchJSON(`/api/compare/teams?id1=${id1}&id2=${id2}&season=${season}`);
    if (!data || !data.team1 || !data.team2) { NBA.showError(el); return; }

    const t1 = data.team1, t2 = data.team2;
    const cats = [
        { key: 'wins', label: 'Wins' }, { key: 'losses', label: 'Losses' },
        { key: 'ppg', label: 'PPG' }, { key: 'rpg', label: 'RPG' }, { key: 'apg', label: 'APG' },
        { key: 'fg_pct', label: 'FG%', pct: true }, { key: 'fg3_pct', label: '3PT%', pct: true }
    ];

    el.innerHTML = `
        <div class="row g-4 mb-4">
            <div class="col-md-6 text-center">
                <img src="/static/images/logos/${t1.abbreviation}.png" style="width:60px;height:60px;object-fit:contain;" onerror="this.onerror=null;this.src='/static/images/player-placeholder.svg';">
                <h3 style="color:var(--accent-cyan);">${t1.full_name || t1.abbreviation}</h3>
            </div>
            <div class="col-md-6 text-center">
                <img src="/static/images/logos/${t2.abbreviation}.png" style="width:60px;height:60px;object-fit:contain;" onerror="this.onerror=null;this.src='/static/images/player-placeholder.svg';">
                <h3 style="color:var(--accent-purple);">${t2.full_name || t2.abbreviation}</h3>
            </div>
        </div>
        <div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>Stat</th><th style="text-align:right;">${t1.full_name || t1.abbreviation}</th><th style="text-align:right;">${t2.full_name || t2.abbreviation}</th></tr></thead>
            <tbody>${cats.map(c => {
                const v1 = c.pct ? (t1[c.key] ? (t1[c.key]*100).toFixed(1)+'%' : '-') : NBA.fmt(t1[c.key], 0);
                const v2 = c.pct ? (t2[c.key] ? (t2[c.key]*100).toFixed(1)+'%' : '-') : NBA.fmt(t2[c.key], 0);
                return `<tr><td>${c.label}</td><td class="num" style="text-align:right;">${v1}</td><td class="num" style="text-align:right;">${v2}</td></tr>`;
            }).join('')}</tbody>
        </table></div>`;
}
</script>
