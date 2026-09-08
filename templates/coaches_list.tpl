% rebase('base.tpl', title='Coaches', page='coaches')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>Coaches</h2>
    </div>

    <!-- Rankings -->
    <div class="card mb-4">
        <div class="card-header"><h5><i class="bi bi-trophy me-2"></i>Coach Rankings (Min 3 Seasons)</h5></div>
        <div class="card-body" id="rankingsBody">
            <div class="skeleton skeleton-card" style="height:200px;"></div>
        </div>
    </div>

    <!-- All coaches -->
    <div class="card">
        <div class="card-header"><h5><i class="bi bi-clipboard-data me-2"></i>All Coaches</h5></div>
        <div class="card-body" id="coachesBody">
            <div class="skeleton skeleton-card" style="height:300px;"></div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async () => {
    // Rankings
    const rankings = await NBA.fetchJSON('/coach/api/rankings');
    const rb = document.getElementById('rankingsBody');
    if (rankings && rankings.length) {
        rb.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>#</th><th>Coach</th><th>Seasons</th><th>Wins</th><th>Losses</th><th>Win%</th></tr></thead>
            <tbody>${rankings.map((c, i) => `<tr style="cursor:pointer;" onclick="location.href='/coach/${c.coach_id}'">
                <td class="num">${i+1}</td>
                <td><strong>${c.coach_name}</strong></td>
                <td class="num">${c.total_seasons}</td>
                <td class="num win">${c.total_wins}</td>
                <td class="num loss">${c.total_losses}</td>
                <td class="num" style="color:var(--accent-cyan);">${c.win_pct ? (c.win_pct * 100).toFixed(1) + '%' : '-'}</td>
            </tr>`).join('')}</tbody></table></div>`;
    } else { NBA.showError(rb, 'No rankings available'); }

    // All coaches
    const all = await NBA.fetchJSON('/coach/api/all');
    const cb = document.getElementById('coachesBody');
    if (all && all.length) {
        cb.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
            <thead><tr><th>Coach</th><th>Seasons</th></tr></thead>
            <tbody>${all.map(c => `<tr style="cursor:pointer;" onclick="location.href='/coach/${c.coach_id}'">
                <td><strong>${c.coach_name}</strong></td>
                <td class="num">${c.seasons || '-'}</td>
            </tr>`).join('')}</tbody></table></div>`;
    } else { NBA.showError(cb, 'No coach data'); }
});
</script>
