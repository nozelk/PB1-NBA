% rebase('base.tpl', title='Teams', page='teams')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>All Teams</h2>
        <div class="pill-group" id="confFilter">
            <button class="pill active" data-conf="all">All</button>
            <button class="pill" data-conf="East">East</button>
            <button class="pill" data-conf="West">West</button>
        </div>
    </div>

    <div class="teams-grid" id="teamsGrid">
        <!-- skeleton -->
        % for _ in range(30):
        <div class="skeleton skeleton-card" style="height:100px;"></div>
        % end
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async () => {
    const data = await NBA.fetchJSON('/team/api/all');
    if (!data) { NBA.showError(document.getElementById('teamsGrid')); return; }

    let allTeams = data;
    renderTeams(allTeams);

    // Conference filter
    document.querySelectorAll('#confFilter .pill').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#confFilter .pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const conf = btn.dataset.conf;
            renderTeams(conf === 'all' ? allTeams : allTeams.filter(t => t.conference === conf));
        });
    });
});

function renderTeams(teams) {
    const grid = document.getElementById('teamsGrid');
    grid.innerHTML = teams.map(t => `
        <a href="/team/${t.team_id}" class="card animate-in" style="text-decoration:none;color:inherit;">
            <div class="card-body d-flex align-items-center gap-3">
                <img src="/static/images/logos/${t.abbreviation}.png" alt="${t.abbreviation}"
                     style="width:55px;height:55px;object-fit:contain;"
                     onerror="this.src='https://cdn.nba.com/logos/nba/${t.team_id}/primary/L/logo.svg'">
                <div>
                    <div style="font-family:var(--font-display);font-size:1rem;letter-spacing:0.5px;">${t.full_name}</div>
                    <div style="display:flex;gap:8px;margin-top:4px;">
                        <span class="badge-conference">${t.conference || ''}</span>
                        <span style="color:var(--text-muted);font-size:0.75rem;">${t.division || ''}</span>
                    </div>
                </div>
            </div>
        </a>
    `).join('');
}
</script>
