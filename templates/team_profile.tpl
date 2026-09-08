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
}

async function loadOverview(el) {
    const seasons = await NBA.fetchJSON(`/team/api/${TEAM_ID}/seasons`);
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

</script>
