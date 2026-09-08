% rebase('base.tpl', title='NBA Analytics', page='home')
<div class="page-container">
    <div class="section-header"><h1>NBA Analytics</h1></div>
    <p class="mb-4" style="color:var(--text-secondary);">Explore NBA history, season statistics and performance.</p>
    <div class="stats-grid mb-4">
        <div class="stat-card"><div class="stat-value">{{ totals['seasons'] }}</div><div class="stat-label">Seasons</div></div>
    </div>
    <div class="row g-4">
        <div class="col-12"><div class="card p-4"><h2>NBA history</h2><p>Season records and statistics from the NBA.</p><img src="/static/images/LogoNBA.png" alt="NBA" style="max-width:180px;"></div></div>
    </div>
</div>
