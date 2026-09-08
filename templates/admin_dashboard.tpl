% rebase('base.tpl', title='Admin Dashboard', page='admin')

<div class="page-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div class="section-header" style="margin-bottom:0;">
            <h2><span class="section-icon"></span>Admin Dashboard</h2>
        </div>
        <div>
            <button class="btn btn-accent me-2" id="btnRefreshAll" onclick="refreshAll()">
                <i class="bi bi-arrow-repeat me-1"></i>Refresh All Data
            </button>
            <a href="/nba/admin/logout" class="btn btn-outline-secondary">
                <i class="bi bi-box-arrow-right me-1"></i>Logout
            </a>
        </div>
    </div>

    <!-- Status Cards -->
    <div class="row g-3 mb-4" id="statusCards">
        <div class="col-12"><div class="skeleton skeleton-card" style="height:200px;"></div></div>
    </div>

    <!-- Season Coverage -->
    <div class="card mb-4">
        <div class="card-header"><h5><i class="bi bi-calendar-range me-2"></i>Season Coverage</h5></div>
        <div class="card-body" id="coverageBody">
            <div class="skeleton skeleton-card" style="height:150px;"></div>
        </div>
    </div>

    <!-- Individual Refresh Buttons -->
    <div class="card mb-4">
        <div class="card-header"><h5><i class="bi bi-gear me-2"></i>Data Collection Tasks</h5></div>
        <div class="card-body" id="tasksBody"></div>
    </div>

    <!-- ★ Player Game Stats per Season -->
    <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5><i class="bi bi-clipboard-data me-2" style="color:var(--accent-orange,#ff9500);"></i>Player Game Stats <span style="font-size:0.6em;color:var(--text-muted);font-weight:400;">per season</span></h5>
            <button class="btn btn-outline-secondary btn-sm" onclick="loadPlayerStatsCoverage()"><i class="bi bi-arrow-repeat me-1"></i>Refresh</button>
        </div>
        <div class="card-body" id="playerStatsBody">
            <p style="color:var(--text-muted);">Loading coverage...</p>
        </div>
    </div>

    <!-- Backups -->
    <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
            <h5><i class="bi bi-archive me-2"></i>Database Backups</h5>
            <button class="btn btn-outline-secondary btn-sm" onclick="loadBackups()"><i class="bi bi-arrow-repeat me-1"></i>Refresh</button>
        </div>
        <div class="card-body" id="backupsBody">
            <p style="color:var(--text-muted);">Click refresh to load backups.</p>
        </div>
    </div>

    <!-- Task Log -->
    <div class="card">
        <div class="card-header"><h5><i class="bi bi-terminal me-2"></i>Task Status</h5></div>
        <div class="card-body" id="taskLog">
            <p style="color:var(--text-muted);">No tasks running.</p>
        </div>
    </div>

    <!-- Staging Preview Modal -->
    <div id="stagingModal" style="display:none;position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,0.7);backdrop-filter:blur(4px);">
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--bg-primary);border:1px solid var(--accent-cyan);border-radius:12px;padding:1.5rem;min-width:450px;max-width:600px;box-shadow:0 20px 60px rgba(0,0,0,0.5);">
            <h4 style="color:var(--accent-cyan);font-family:var(--font-display);margin-bottom:1rem;">
                <i class="bi bi-search me-2"></i>Preview Changes
            </h4>
            <p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:0.5rem;" id="stagingTaskName"></p>
            <div id="stagingPreviewBody" style="font-family:var(--font-mono);font-size:0.85rem;margin-bottom:1rem;"></div>
            <div class="d-flex gap-2 justify-content-end">
                <button class="btn btn-outline-secondary" onclick="cancelStaging()" id="btnCancelStaging">
                    <i class="bi bi-x-circle me-1"></i>Cancel
                </button>
                <button class="btn btn-accent" onclick="confirmStaging()" id="btnConfirmStaging">
                    <i class="bi bi-check-circle me-1"></i>Confirm Insert
                </button>
            </div>
        </div>
    </div>
</div>

<script>
function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
const TASKS = [
    {key: 'teams',              label: 'Teams (30 teams)',              icon: 'bi-people'},
    {key: 'team_season_stats',  label: 'Team Season Stats',            icon: 'bi-bar-chart'},
    {key: 'players',            label: 'Players & Season Stats',       icon: 'bi-person-badge'},
    {key: 'player_details',     label: 'Player Details (slow)',        icon: 'bi-person-lines-fill'},
    {key: 'games',              label: 'Games (very slow)',            icon: 'bi-controller'},
    {key: 'player_game_stats',  label: 'Player Game Stats (very slow)',icon: 'bi-clipboard-data'},
    {key: 'rosters',            label: 'Rosters',                      icon: 'bi-list-ol'},
    {key: 'coaches',            label: 'Coaches',                      icon: 'bi-clipboard-check'},
    {key: 'salaries',           label: 'Salaries (scraping)',          icon: 'bi-currency-dollar'},
    {key: 'awards',             label: 'Awards',                       icon: 'bi-trophy'},
];

let _currentStagedTask = null;

document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    renderTasks();
    loadPlayerStatsCoverage();
    setInterval(pollTaskStatus, 3000);
    setInterval(loadPlayerStatsCoverage, 10000);
});

async function loadStatus() {
    const data = await NBA.fetchJSON('/nba/admin/api/status');
    if (!data) return;

    const cards = document.getElementById('statusCards');
    const counts = data.counts;
    const items = Object.entries(counts).map(([table, count]) => {
        const ok = count > 0;
        return `<div class="col-sm-6 col-md-4 col-lg-3">
            <div class="stat-card" style="border-color:${ok ? 'var(--accent-cyan)' : 'var(--accent-red)'};">
                <div class="stat-label">${table.replace(/_/g, ' ')}</div>
                <div class="stat-value" style="color:${ok ? 'var(--accent-cyan)' : 'var(--accent-red)'};">${NBA.fmt(count)}</div>
                <div style="font-size:0.75rem;color:${ok ? 'var(--accent-green,#0f0)' : 'var(--accent-red)'};">
                    ${ok ? '<i class="bi bi-check-circle"></i> OK' : '<i class="bi bi-exclamation-triangle"></i> Empty'}
                </div>
            </div>
        </div>`;
    });
    cards.innerHTML = items.join('');

    const cov = document.getElementById('coverageBody');
    const range = data.season_range;
    let html = `<p style="color:var(--text-secondary);">Season range: <strong style="color:var(--accent-cyan);">${seasonLabel(range.start)}</strong> to <strong style="color:var(--accent-cyan);">${seasonLabel(range.end)}</strong></p>`;

    for (const [table, seasons] of Object.entries(data.season_coverage)) {
        html += `<div class="mb-3"><h6 style="color:var(--text-secondary);">${table.replace(/_/g, ' ')}</h6><div class="d-flex flex-wrap gap-1">`;
        for (let y = range.start; y <= range.end; y++) {
            const c = seasons[y] || 0;
            const color = c > 0 ? 'var(--accent-cyan)' : 'var(--accent-red)';
            html += `<span class="badge" style="background:${c > 0 ? 'rgba(0,240,255,0.15)' : 'rgba(255,45,85,0.15)'};color:${color};font-size:0.7rem;padding:4px 6px;" title="${c} rows">${seasonLabel(y)} (${c})</span>`;
        }
        html += `</div></div>`;
    }

    if (data.missing_player_details > 0) {
        html += `<p style="color:var(--accent-red);"><i class="bi bi-exclamation-triangle me-1"></i>${data.missing_player_details} players missing details (height, country, etc.)</p>`;
    }
    cov.innerHTML = html;
}

function renderTasks() {
    const el = document.getElementById('tasksBody');
    el.innerHTML = `<div class="row g-2">${TASKS.map(t =>
        `<div class="col-sm-6 col-lg-4">
            <button class="btn btn-outline-secondary w-100 text-start task-btn" id="taskBtn_${t.key}" onclick="refreshTask('${t.key}')">
                <i class="bi ${t.icon} me-2"></i>${t.label}
            </button>
        </div>`
    ).join('')}</div>`;
}

async function refreshTask(task) {
    const btn = document.getElementById('taskBtn_' + task);
    if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Collecting (staging)...'; }

    const res = await fetch('/nba/admin/api/refresh', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({task})
    });
    const data = await res.json();
    updateLog({[task]: {status: data.status, message: data.message || 'Collecting into staging...'}});
}

async function refreshAll() {
    if (!confirm('This will create a backup and run ALL collection tasks directly into the database. Continue?')) return;
    const btn = document.getElementById('btnRefreshAll');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Running...';

    const res = await fetch('/nba/admin/api/refresh/all', {
        method: 'POST', headers: {'Content-Type': 'application/json'}
    });
    const data = await res.json();
    updateLog({all: {status: data.status, message: 'Full pipeline started (with backup)'}});
}

function showStagingModal(task, preview) {
    _currentStagedTask = task;
    const taskInfo = TASKS.find(t => t.key === task);
    document.getElementById('stagingTaskName').textContent = taskInfo ? taskInfo.label : task;

    let html = '<table style="width:100%;border-collapse:collapse;">';
    html += '<tr style="border-bottom:1px solid var(--border-color);"><th style="padding:6px 8px;text-align:left;color:var(--text-muted);font-size:0.75rem;">TABLE</th><th style="padding:6px 8px;text-align:right;color:var(--text-muted);font-size:0.75rem;">BEFORE</th><th style="padding:6px 8px;text-align:right;color:var(--text-muted);font-size:0.75rem;">AFTER</th><th style="padding:6px 8px;text-align:right;color:var(--text-muted);font-size:0.75rem;">CHANGE</th></tr>';

    const before = preview.before || {};
    const after = preview.after || {};
    for (const table of Object.keys(after)) {
        const b = before[table] || 0;
        const a = after[table] || 0;
        const diff = a - b;
        const diffColor = diff > 0 ? 'var(--accent-green,#0f0)' : diff < 0 ? 'var(--accent-red)' : 'var(--text-muted)';
        const diffText = diff > 0 ? `+${diff}` : diff === 0 ? '0' : `${diff}`;
        html += `<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
            <td style="padding:8px;color:var(--text-primary);">${table.replace(/_/g, ' ')}</td>
            <td style="padding:8px;text-align:right;color:var(--text-secondary);">${NBA.fmt(b)}</td>
            <td style="padding:8px;text-align:right;color:var(--accent-cyan);">${NBA.fmt(a)}</td>
            <td style="padding:8px;text-align:right;color:${diffColor};font-weight:600;">${diffText}</td>
        </tr>`;
    }
    html += '</table>';
    document.getElementById('stagingPreviewBody').innerHTML = html;
    document.getElementById('stagingModal').style.display = '';
}

async function confirmStaging() {
    if (!_currentStagedTask) return;
    const btn = document.getElementById('btnConfirmStaging');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Applying...';

    const res = await fetch('/nba/admin/api/refresh/confirm', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({task: _currentStagedTask})
    });
    const data = await res.json();
    document.getElementById('stagingModal').style.display = 'none';
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-check-circle me-1"></i>Confirm Insert';

    if (data.status === 'confirmed') {
        updateLog({[_currentStagedTask]: {status: 'done', message: `Applied! Backup: ${data.backup}`}});
        loadStatus();
    } else {
        updateLog({[_currentStagedTask]: {status: 'error', message: data.error || 'Confirm failed'}});
    }

    // Re-enable task button
    const taskBtn = document.getElementById('taskBtn_' + _currentStagedTask);
    const t = TASKS.find(x => x.key === _currentStagedTask);
    if (taskBtn && t) { taskBtn.disabled = false; taskBtn.innerHTML = `<i class="bi ${t.icon} me-2"></i>${t.label}`; }

    _currentStagedTask = null;
}

async function cancelStaging() {
    if (!_currentStagedTask) { document.getElementById('stagingModal').style.display = 'none'; return; }

    await fetch('/nba/admin/api/refresh/cancel', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({task: _currentStagedTask})
    });
    document.getElementById('stagingModal').style.display = 'none';
    updateLog({[_currentStagedTask]: {status: 'cancelled', message: 'Cancelled — no changes made.'}});

    // Re-enable task button
    const taskBtn = document.getElementById('taskBtn_' + _currentStagedTask);
    const t = TASKS.find(x => x.key === _currentStagedTask);
    if (taskBtn && t) { taskBtn.disabled = false; taskBtn.innerHTML = `<i class="bi ${t.icon} me-2"></i>${t.label}`; }

    _currentStagedTask = null;
}

async function pollTaskStatus() {
    const res = await fetch('/nba/admin/api/refresh/status');
    if (!res.ok) return;
    const data = await res.json();
    updateLog(data);

    for (const [task, info] of Object.entries(data)) {
        const btn = document.getElementById('taskBtn_' + task);

        // Show preview modal when staging is complete
        if (info.status === 'staged' && info.preview) {
            if (btn) { btn.innerHTML = '<i class="bi bi-search me-2"></i>Review pending...'; }
            // Only open modal if not already open for another task
            if (!_currentStagedTask || _currentStagedTask === task) {
                showStagingModal(task, info.preview);
            }
        }

        // Re-enable buttons for completed/error/cancelled tasks
        if (btn && !['running', 'staged'].includes(info.status)) {
            const t = TASKS.find(x => x.key === task);
            if (t) { btn.disabled = false; btn.innerHTML = `<i class="bi ${t.icon} me-2"></i>${t.label}`; }
        }
    }

    // Re-enable refresh all button
    if (!data.all || data.all.status !== 'running') {
        const btn = document.getElementById('btnRefreshAll');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i>Refresh All Data';
        }
    }

    // Reload counts if something finished
    const anyDone = Object.values(data).some(v => v.status === 'done');
    if (anyDone) loadStatus();
}

function updateLog(data) {
    const el = document.getElementById('taskLog');
    let html = '<div style="font-family:var(--font-mono);font-size:0.8rem;">';
    for (const [task, info] of Object.entries(data)) {
        const color = info.status === 'done' ? 'var(--accent-green,#0f0)' :
                      info.status === 'error' ? 'var(--accent-red)' :
                      info.status === 'running' ? 'var(--accent-cyan)' :
                      info.status === 'staged' ? 'var(--accent-orange,#ff9500)' :
                      info.status === 'cancelled' ? 'var(--text-muted)' : 'var(--text-muted)';
        const icon = info.status === 'done' ? 'bi-check-circle' :
                     info.status === 'error' ? 'bi-x-circle' :
                     info.status === 'running' ? 'bi-arrow-repeat' :
                     info.status === 'staged' ? 'bi-search' :
                     info.status === 'cancelled' ? 'bi-slash-circle' : 'bi-dash';
        html += `<div class="mb-1" style="color:${color};"><i class="bi ${icon} me-1"></i><strong>${task}</strong>: ${info.message || info.status}</div>`;
    }
    html += '</div>';
    el.innerHTML = html;
}

async function loadBackups() {
    const data = await NBA.fetchJSON('/nba/admin/api/backups');
    const el = document.getElementById('backupsBody');
    if (!data || !data.length) {
        el.innerHTML = '<p style="color:var(--text-muted);">No backups found.</p>';
        return;
    }
    let html = '<div style="max-height:200px;overflow-y:auto;">';
    for (const b of data) {
        html += `<div class="d-flex justify-content-between align-items-center" style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            <div>
                <span style="font-family:var(--font-mono);font-size:0.8rem;color:var(--text-primary);">${b.filename}</span>
                <span style="font-size:0.7rem;color:var(--text-muted);margin-left:8px;">${b.size_mb} MB</span>
            </div>
            <button class="btn btn-outline-secondary btn-sm" onclick="restoreBackup('${b.filename}')">
                <i class="bi bi-arrow-counterclockwise me-1"></i>Restore
            </button>
        </div>`;
    }
    html += '</div>';
    el.innerHTML = html;
}

async function restoreBackup(filename) {
    if (!confirm('Restore database from ' + filename + '? A safety backup will be created first.')) return;
    const res = await fetch('/nba/admin/api/backups/restore', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({filename})
    });
    const data = await res.json();
    if (data.status === 'restored') {
        alert('Restored from ' + filename + '! Safety backup: ' + data.safety_backup);
        loadStatus();
        loadBackups();
    } else {
        alert('Error: ' + (data.error || 'Unknown error'));
    }
}

// ── PLAYER GAME STATS PER SEASON ──────────────────────────
async function loadPlayerStatsCoverage() {
    const data = await NBA.fetchJSON('/nba/admin/api/player-stats/coverage');
    if (!data || !data.seasons) return;
    const el = document.getElementById('playerStatsBody');
    const active = data.active_tasks || {};

    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px;">';
    for (const s of data.seasons) {
        const yr = s.season;
        const label = seasonLabel(yr);
        const isRunning = active[yr];
        const pct = s.expected_players > 0 ? Math.round(s.collected_players / s.expected_players * 100) : 0;

        let statusColor, statusIcon, statusText;
        if (isRunning) {
            statusColor = 'var(--accent-cyan)';
            statusIcon = 'bi-arrow-repeat';
            statusText = 'Collecting...';
        } else if (s.status === 'complete') {
            statusColor = 'var(--accent-green,#0f0)';
            statusIcon = 'bi-check-circle-fill';
            statusText = 'Complete';
        } else if (s.status === 'partial') {
            statusColor = 'var(--accent-orange,#ff9500)';
            statusIcon = 'bi-exclamation-circle';
            statusText = `${s.missing_players} missing`;
        } else {
            statusColor = 'var(--accent-red)';
            statusIcon = 'bi-x-circle';
            statusText = 'No data';
        }

        // Progress bar
        const barColor = s.status === 'complete' ? 'var(--accent-green,#0f0)' : s.status === 'partial' ? 'var(--accent-orange,#ff9500)' : 'var(--accent-red)';

        html += `<div style="background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:8px;padding:10px 12px;position:relative;overflow:hidden;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <span style="font-family:var(--font-display);font-size:0.9rem;color:var(--text-primary);font-weight:600;">${label}</span>
                <span style="font-size:0.7rem;color:${statusColor};"><i class="bi ${statusIcon} me-1"></i>${statusText}</span>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">
                <span>${NBA.fmt(s.collected_players)}/${NBA.fmt(s.expected_players)} players</span>
                <span>${NBA.fmt(s.total_rows)} rows</span>
            </div>
            <div style="height:4px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;margin-bottom:8px;">
                <div style="height:100%;width:${pct}%;background:${barColor};border-radius:2px;transition:width .5s;"></div>
            </div>
            <div style="display:flex;gap:4px;">`;

        if (isRunning) {
            html += `<button class="btn btn-outline-secondary btn-sm w-100" disabled>
                <span class="spinner-border spinner-border-sm me-1"></span>Running...
            </button>`;
        } else if (s.status === 'empty') {
            html += `<button class="btn btn-accent btn-sm w-100" onclick="collectPlayerStats(${yr}, false)">
                <i class="bi bi-download me-1"></i>Collect All
            </button>`;
        } else if (s.status === 'partial') {
            html += `<button class="btn btn-accent btn-sm" style="flex:1;" onclick="collectPlayerStats(${yr}, true)">
                <i class="bi bi-arrow-repeat me-1"></i>Retry Missing
            </button>
            <button class="btn btn-outline-secondary btn-sm" style="flex:1;" onclick="collectPlayerStats(${yr}, false)">
                <i class="bi bi-download me-1"></i>Full Recollect
            </button>`;
        } else {
            html += `<button class="btn btn-outline-secondary btn-sm w-100" onclick="collectPlayerStats(${yr}, false)">
                <i class="bi bi-arrow-repeat me-1"></i>Recollect
            </button>`;
        }

        html += `</div></div>`;
    }
    html += '</div>';
    el.innerHTML = html;
}

async function collectPlayerStats(season, retry) {
    const label = seasonLabel(season);
    const action = retry ? 'retry missing players' : 'collect all game stats';
    if (!confirm(`${action} for ${label}? This may take a while.`)) return;

    const res = await fetch('/nba/admin/api/player-stats/collect', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({season, retry})
    });
    const data = await res.json();
    updateLog({['game_stats_' + season]: {status: data.status, message: data.message || `Started for ${label}`}});
    loadPlayerStatsCoverage();
}
</script>
