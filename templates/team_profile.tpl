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
             onerror="this.src='https://cdn.nba.com/logos/nba/${TEAM_ID}/primary/L/logo.svg'">
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
                 style="width:28px;height:28px;border-radius:50%;object-fit:cover;margin-right:6px;" onerror="this.style.display='none'">
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
                         onerror="this.parentElement.innerHTML='<i class=\\'bi bi-person\\' style=\\'font-size:1.2rem;color:var(--text-muted);display:flex;align-items:center;justify-content:center;height:100%;\\'></i>'">
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

</script>
