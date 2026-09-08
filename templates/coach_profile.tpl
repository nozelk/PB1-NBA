% rebase('base.tpl', title='Coach Profile', page='coaches')

<div class="page-container">
    <div class="profile-header" id="coachHeader">
        <div style="width:80px;height:80px;background:var(--bg-secondary);border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid var(--accent-cyan);">
            <i class="bi bi-clipboard-data" style="font-size:2rem;color:var(--accent-cyan);"></i>
        </div>
        <div class="profile-info">
            <div class="skeleton skeleton-title"></div>
        </div>
    </div>

    <div class="row g-4">
        <!-- Seasons -->
        <div class="col-lg-7">
            <div class="card">
                <div class="card-header"><h5>Season History</h5></div>
                <div class="card-body" id="seasonsBody"><div class="skeleton skeleton-card"></div></div>
            </div>
        </div>
        <!-- Charts -->
        <div class="col-lg-5">
            <div class="chart-container">
                <h5 style="color:var(--accent-cyan);font-family:var(--font-display);font-size:0.85rem;letter-spacing:1px;text-transform:uppercase;margin-bottom:1rem;">
                    Wins by Season
                </h5>
                <canvas id="chartWins" height="280"></canvas>
            </div>
        </div>
    </div>

    <!-- Impact -->
    <div class="card mt-4">
        <div class="card-header"><h5>Coach Impact (Performance Change)</h5></div>
        <div class="card-body" id="impactBody"><div class="skeleton skeleton-card"></div></div>
    </div>
</div>

<script>
function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
const CID = window.location.pathname.split('/').filter(Boolean).pop();

document.addEventListener('DOMContentLoaded', async () => {
    const info = await NBA.fetchJSON(`/coach/api/${CID}`);
    if (!info) { NBA.showError(document.getElementById('coachHeader'), 'Coach not found'); return; }

    // Header
    document.querySelector('#coachHeader .profile-info').innerHTML = `
        <h1>${info.coach_name}</h1>
        <div class="profile-meta">
            <span style="color:var(--text-secondary);">${info.seasons ? info.seasons.length + ' seasons' : ''}</span>
        </div>`;

    // Seasons table
    const sb = document.getElementById('seasonsBody');
    if (info.seasons && info.seasons.length) {
        sb.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>Season</th><th>Team</th><th>W</th><th>L</th><th>Win%</th><th>Conf Rank</th></tr></thead>
            <tbody>${info.seasons.map(s => `<tr>
                <td class="num">${seasonLabel(s.season)}</td>
                <td>${s.team_name || '-'}</td>
                <td class="num win">${s.wins || 0}</td>
                <td class="num loss">${s.losses || 0}</td>
                <td class="num">${s.wins && s.losses ? ((s.wins/(s.wins+s.losses))*100).toFixed(1)+'%' : '-'}</td>
                <td class="num">${s.conf_rank || '-'}</td>
            </tr>`).join('')}</tbody></table></div>`;

        // Chart – chronological order (ASC)
        const chartSeasons = [...info.seasons].reverse();
        const labels = chartSeasons.map(s => seasonLabel(s.season));
        const wins = chartSeasons.map(s => s.wins || 0);
        const ctx = document.getElementById('chartWins').getContext('2d');
        new Chart(ctx, {
            type: 'bar', data: { labels, datasets: [{ label: 'Wins', data: wins, backgroundColor: NBA.CYAN+'80', borderColor: NBA.CYAN, borderWidth: 1, borderRadius: 4 }] },
            options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(42,42,68,0.3)' }, beginAtZero: true }, x: { grid: { display: false } } } }
        });
    } else { sb.innerHTML = '<p style="color:var(--text-muted);">No season data.</p>'; }

    // Impact
    const impact = await NBA.fetchJSON(`/coach/api/${CID}/impact`);
    const ib = document.getElementById('impactBody');
    if (impact && impact.length) {
        ib.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>Season</th><th>Team</th><th>Wins</th><th>Prev Wins</th><th>Change</th></tr></thead>
            <tbody>${impact.map(r => {
                const change = r.win_change;
                const cls = change > 0 ? 'positive' : change < 0 ? 'negative' : '';
                return `<tr>
                    <td class="num">${seasonLabel(r.season)}</td>
                    <td>${r.team_name || '-'}</td>
                    <td class="num">${r.wins}</td>
                    <td class="num">${r.prev_wins != null ? r.prev_wins : '-'}</td>
                    <td class="num ${cls}">${change != null ? (change > 0 ? '+' : '') + change : '-'}</td>
                </tr>`;
            }).join('')}</tbody></table></div>`;
    } else { ib.innerHTML = '<p style="color:var(--text-muted);">No impact data.</p>'; }
});
</script>
