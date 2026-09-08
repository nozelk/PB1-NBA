% rebase('base.tpl', title='Players', page='players')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>Players</h2>
        <div class="d-flex gap-2 align-items-center">
            <input type="text" id="playerSearch" class="form-control" placeholder="Filter players..." style="width:220px;">
            <select id="posFilter" class="form-select" style="width:auto;">
                <option value="all">All Positions</option>
                <option value="Guard">Guard</option>
                <option value="Forward">Forward</option>
                <option value="Center">Center</option>
            </select>
        </div>
    </div>

    <div id="playersTable" style="overflow-x:auto;">
        <div class="skeleton skeleton-card" style="height:400px;"></div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async () => {
    const data = await NBA.fetchJSON('/player/api/all');
    if (!data) { NBA.showError(document.getElementById('playersTable')); return; }

    let allPlayers = data;
    renderPlayers(allPlayers);

    document.getElementById('playerSearch').addEventListener('input', applyFilters);
    document.getElementById('posFilter').addEventListener('change', applyFilters);

    function applyFilters() {
        const q = document.getElementById('playerSearch').value.toLowerCase();
        const pos = document.getElementById('posFilter').value;
        let filtered = allPlayers;
        if (q) filtered = filtered.filter(p => p.full_name.toLowerCase().includes(q));
        if (pos !== 'all') filtered = filtered.filter(p => (p.position || '').includes(pos));
        renderPlayers(filtered);
    }
});

function renderPlayers(players) {
    const el = document.getElementById('playersTable');
    if (!players.length) { el.innerHTML = '<p style="color:var(--text-muted);">No players found.</p>'; return; }

    el.innerHTML = `
        <table class="table-dark-custom">
            <thead><tr>
                <th>Player</th><th>Position</th><th>Team</th><th>Seasons</th>
            </tr></thead>
            <tbody>
                ${players.slice(0, 200).map(p => `<tr style="cursor:pointer;" onclick="location.href='/player/${p.player_id}'">
                    <td><strong>${p.full_name}</strong></td>
                    <td><span class="badge-position">${p.position || '-'}</span></td>
                    <td>${p.team_abbreviation || p.last_team || '-'}</td>
                    <td class="num">${p.from_year || '?'} - ${p.to_year || '?'}</td>
                </tr>`).join('')}
            </tbody>
        </table>
        ${players.length > 200 ? `<p style="color:var(--text-muted);font-size:0.8rem;margin-top:1rem;">Showing 200 of ${players.length} players. Use the filter to narrow results.</p>` : ''}`;
}
</script>
