% rebase('base.tpl', title='Data management', page='admin')

<div class="page-container admin-page">
    <header class="page-heading">
        <div><div class="eyebrow">Administration</div><h1>Data management</h1>
            <p>Check what is in your database, collect missing game logs and manage updates.</p></div>
        <div class="heading-actions"><a href="/" class="btn btn-outline-secondary">View dashboard</a>
            <a href="/nba/admin/logout" class="btn btn-outline-secondary">Sign out</a></div>
    </header>
    <nav class="admin-nav" aria-label="Administration sections">
        <a href="#playerCoverage">Player data</a><a href="#collectionTasks">Collection tools</a>
        <a href="#databaseBackups">Backups</a><a href="#taskHistory">Task activity</a>
    </nav>
    <div class="admin-summary" id="coverageSummary">
        <div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-card"></div><div class="skeleton skeleton-card"></div>
    </div>
    <section class="card" id="playerCoverage" aria-labelledby="coverageTitle">
        <div class="coverage-header">
            <div><h2 id="coverageTitle">Player statistics · individual games</h2>
                <p>Season summaries power the averages on player profiles. Game logs store each individual performance.
                    Coverage below compares game counts with the season summaries already in your database.</p></div>
            <button class="btn btn-outline-secondary btn-sm" onclick="loadPlayerStatsCoverage()">Refresh coverage</button>
        </div>
        <div class="coverage-toolbar">
            <div class="d-flex align-items-center gap-2"><label for="coverageFilter" class="coverage-caption">Show</label>
                <select class="form-select" id="coverageFilter" onchange="renderCoverage()">
                    <option value="all">All seasons</option><option value="available">With game logs</option>
                    <option value="missing">Needs attention</option>
                </select></div>
            <p class="coverage-caption" id="coverageUpdated" role="status">Checking stored data…</p>
        </div>
        <div class="card-body" id="playerStatsBody"><p class="empty-state">Loading player data coverage…</p></div>
    </section>
    <details class="inventory">
        <summary>Database inventory &amp; season archive</summary>
        <div class="inventory-content"><div class="row g-3 mb-4" id="statusCards"></div>
            <div id="coverageBody"></div></div>
    </details>
    <section class="card admin-section" id="collectionTasks">
        <div class="card-header"><div><h5>Collection tools</h5>
            <span class="section-note">Choose a dataset to collect and review before applying changes.</span></div>
            <button class="btn btn-outline-secondary btn-sm" id="btnRefreshAll" onclick="refreshAll()">Refresh all data</button></div>
        <div class="card-body" id="tasksBody"></div>
    </section>
    <section class="card admin-section" id="databaseBackups">
        <div class="card-header"><div><h5>Database backups</h5><span class="section-note">View saved copies and restore a previous database.</span></div>
            <button class="btn btn-outline-secondary btn-sm" onclick="loadBackups()">Load backups</button></div>
        <div class="card-body" id="backupsBody"><p class="coverage-caption">Select “Load backups” to view saved copies.</p></div>
    </section>
    <section class="card admin-section" id="taskHistory">
        <div class="card-header"><h5>Task activity</h5></div>
        <div class="card-body" id="taskLog" aria-live="polite"><p class="coverage-caption">No collection tasks running.</p></div>
    </section>
    <div id="stagingModal" class="admin-modal" role="dialog" aria-modal="true" aria-labelledby="stagingTitle" style="display:none;">
        <div class="admin-modal__content">
            <h4 id="stagingTitle">Review collected data</h4>
            <p class="coverage-caption mb-3" id="stagingTaskName"></p><div id="stagingPreviewBody"></div>
            <div class="d-flex gap-2 justify-content-end">
                <button class="btn btn-outline-secondary" onclick="cancelStaging()" id="btnCancelStaging">Cancel</button>
                <button class="btn btn-accent" onclick="confirmStaging()" id="btnConfirmStaging">Apply changes</button>
            </div>
        </div>
    </div>
</div>
<script src="/static/js/admin.js?v=9" defer></script>
