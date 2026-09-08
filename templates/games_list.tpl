% rebase('base.tpl', title='Games', page='games')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>Games</h2>
    </div>

    <!-- Tabs -->
    <div class="nav-tabs-nba" style="flex-wrap:wrap;">
        <button class="tab-btn active" data-tab="recent">Recent Games</button>
        <button class="tab-btn" data-tab="highest">Highest Scoring</button>
        <button class="tab-btn" data-tab="blowouts">Biggest Blowouts</button>
        <button class="tab-btn" data-tab="closest">Closest Games</button>
        <button class="tab-btn" data-tab="performances">Top Performances</button>
    </div>

    <!-- Filters -->
    <div class="d-flex gap-3 align-items-center mb-4 flex-wrap">
        <select id="seasonSel" class="form-select" style="width:auto;"></select>
        <select id="teamSel" class="form-select" style="width:auto;">
            <option value="">All Teams</option>
        </select>
        <select id="monthSel" class="form-select" style="width:auto;">
            <option value="">All Months</option>
            <option value="OCT">October</option>
            <option value="NOV">November</option>
            <option value="DEC">December</option>
            <option value="JAN">January</option>
            <option value="FEB">February</option>
            <option value="MAR">March</option>
            <option value="APR">April</option>
            <option value="MAY">May</option>
            <option value="JUN">June</option>
        </select>
    </div>

    <div id="gamesContent">
        <div class="skeleton skeleton-card" style="height:400px;"></div>
    </div>
</div>

<script>
function seasonLabel(y) {
    if (!y) return '-';
    const next = (y % 100) + 1;
    return y + '/' + String(next).padStart(2, '0');
}

function fmtDate(d) {
    if (!d) return '';
    return d.charAt(0) + d.slice(1).toLowerCase();
}

document.addEventListener('DOMContentLoaded', async () => {
    const seasons = await NBA.fetchJSON('/api/seasons');
    const sel = document.getElementById('seasonSel');
    // "All" option
    const allOpt = document.createElement('option');
    allOpt.value = 'all'; allOpt.text = 'All Seasons';
    sel.appendChild(allOpt);
    if (seasons) {
        seasons.forEach((s, i) => {
            const opt = document.createElement('option');
            opt.value = s; opt.text = seasonLabel(s);
            if (i === 0) opt.selected = true;
            sel.appendChild(opt);
        });
    }

    const teams = await NBA.fetchJSON('/team/api/all');
    const tsel = document.getElementById('teamSel');
    if (teams) {
        teams.sort((a, b) => (a.full_name || '').localeCompare(b.full_name || ''));
        teams.forEach(t => {
            const opt = document.createElement('option');
            opt.value = t.team_id; opt.text = t.full_name;
            tsel.appendChild(opt);
        });
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadTab();
        });
    });

    sel.addEventListener('change', loadTab);
    tsel.addEventListener('change', loadTab);
    document.getElementById('monthSel').addEventListener('change', loadTab);
    loadTab();
});

function activeTab() { return document.querySelector('.tab-btn.active')?.dataset.tab || 'recent'; }

async function loadTab() {
    const tab = activeTab();
    const season = document.getElementById('seasonSel').value;
    const team = document.getElementById('teamSel').value;
    const month = document.getElementById('monthSel').value;
    const el = document.getElementById('gamesContent');
    NBA.showLoading(el);

    const tp = team ? '&team_id='+team : '';
    const mp = month ? '&month='+month : '';
    let url = '';
    if (tab === 'recent') url = `/games/api/list?season=${season}&limit=200${tp}${mp}`;
    else if (tab === 'highest') url = `/games/api/highest-scoring?season=${season}&limit=100${tp}`;
    else if (tab === 'blowouts') url = `/games/api/biggest-blowouts?season=${season}&limit=100${tp}`;
    else if (tab === 'closest') url = `/games/api/closest-games?season=${season}&limit=100${tp}`;
    else if (tab === 'performances') url = `/games/api/top-performances?season=${season}&limit=50`;

    const data = await NBA.fetchJSON(url);
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No data available.</p>'; return; }

    if (tab === 'performances') {
        el.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>#</th><th>Player</th><th>Date</th><th>Matchup</th><th>PTS</th><th>REB</th><th>AST</th><th>GmSc</th></tr></thead>
            <tbody>${data.map((g, i) => `<tr>
                <td class="num">${i+1}</td>
                <td><a href="/player/${g.player_id}" style="color:var(--text-primary);">${g.player_name || g.full_name || '-'}</a></td>
                <td class="num" style="white-space:nowrap;">${fmtDate(g.game_date)}</td>
                <td>${g.matchup || ''}</td>
                <td class="num"><strong>${g.pts || 0}</strong></td>
                <td class="num">${g.reb || 0}</td>
                <td class="num">${g.ast || 0}</td>
                <td class="num" style="color:var(--accent-cyan);">${NBA.fmt(g.game_score)}</td>
            </tr>`).join('')}</tbody></table></div>`;
    } else {
        const extraH = tab === 'blowouts' ? 'Margin' : tab === 'closest' ? 'Diff' : tab === 'highest' ? 'Total' : '';
        el.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr>
                <th>Date</th><th>Home</th><th colspan="3" style="text-align:center;">Score</th><th>Away</th>
                ${extraH ? '<th>'+extraH+'</th>' : ''}
            </tr></thead>
            <tbody>${data.map(g => {
                const hp = g.home_pts || 0, ap = g.away_pts || 0;
                const homeWin = g.wl === 'W';
                const margin = Math.abs(hp - ap);
                let extra = '';
                if (tab === 'blowouts' || tab === 'closest') extra = `<td class="num">${margin}</td>`;
                else if (tab === 'highest') extra = `<td class="num">${hp+ap}</td>`;
                return `<tr>
                    <td class="num" style="white-space:nowrap;">${fmtDate(g.game_date)}</td>
                    <td><a href="/team/${g.home_team_id}" style="color:var(--text-primary);font-weight:${homeWin?'700':'400'};">${g.home_team || '-'}</a></td>
                    <td class="num" style="text-align:right;color:${homeWin?'var(--accent-cyan)':'var(--text-muted)'}"><strong>${hp}</strong></td>
                    <td class="num" style="text-align:center;color:var(--text-muted);padding:0 2px;">-</td>
                    <td class="num" style="text-align:left;color:${!homeWin?'var(--accent-cyan)':'var(--text-muted)'}"><strong>${ap}</strong></td>
                    <td><a href="/team/${g.away_team_id}" style="color:var(--text-primary);font-weight:${!homeWin?'700':'400'};">${g.away_team || '-'}</a></td>
                    ${extra}
                </tr>`;
            }).join('')}</tbody></table></div>`;
    }
}
</script>