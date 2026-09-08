% rebase('base.tpl', title='NBA Analytics', page='home')
<div class="page-container">
    <div class="section-header"><h1>NBA Analytics</h1></div>
    <p class="mb-4" style="color:var(--text-secondary);">Explore NBA history, season statistics and performance.</p>
    <div class="stats-grid mb-4">
        <div class="stat-card"><div class="stat-value">{{ totals['seasons'] }}</div><div class="stat-label">Seasons</div></div>
        <div class="stat-card"><div class="stat-value">{{ totals['teams'] }}</div><div class="stat-label">Teams</div></div>
        <div class="stat-card"><div class="stat-value">{{ totals['players'] }}</div><div class="stat-label">Players</div></div>
    </div>
    <div class="row g-4">
        <div class="col-md-6"><a class="card p-4 h-100" href="/team/" style="text-decoration:none;"><h2>Teams</h2><p style="color:var(--text-secondary);">Explore teams and their season history.</p></a></div>
        <div class="col-md-6"><a class="card p-4 h-100" href="/player/" style="text-decoration:none;"><h2>Players</h2><p style="color:var(--text-secondary);">Explore player profiles and career statistics.</p></a></div>
    </div>
</div>
