function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
const TASKS = [
    {key: 'teams',              label: 'Teams (30 teams)',              icon: 'bi-people'},
    {key: 'team_season_stats',  label: 'Team season summaries',            icon: 'bi-bar-chart'},
    {key: 'players',            label: 'Players & season summaries',       icon: 'bi-person-badge'},
    {key: 'player_details',     label: 'Player Details (slow)',        icon: 'bi-person-lines-fill'},
    {key: 'games',              label: 'Team game results (slow)',            icon: 'bi-controller'},
    {key: 'player_game_stats',  label: 'Individual player game logs (slow)',icon: 'bi-clipboard-data'},
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
            <div class="stat-card" >
                <div class="stat-label">${table.replace(/_/g, ' ')}</div>
                <div class="stat-value" style="color:${ok ? 'var(--accent-cyan)' : 'var(--accent-red)'};">${NBA.count(count)}</div>
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
            html += `<span class="badge" style="background:${c > 0 ? 'rgba(131,207,197,0.08)' : 'rgba(238,156,156,0.08)'};color:${color};font-size:0.7rem;padding:4px 6px;" title="${c} rows">${seasonLabel(y)} (${c})</span>`;
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
            <td style="padding:8px;text-align:right;color:var(--text-secondary);">${NBA.count(b)}</td>
            <td style="padding:8px;text-align:right;color:var(--accent-cyan);">${NBA.count(a)}</td>
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

// Coverage keeps season summaries separate from individual game logs.
let coverageData = null;
let coverageLoading = false;

async function loadPlayerStatsCoverage() {
    if (coverageLoading) return;
    coverageLoading = true;
    try {
        const data = await NBA.fetchJSON('/nba/admin/api/player-stats/coverage');
        if (!data || !data.seasons) {
            document.getElementById('coverageUpdated').textContent = 'Unable to refresh coverage. Try again.';
            if (!coverageData) document.getElementById('playerStatsBody').innerHTML = '<p class="empty-state">Coverage could not be loaded.</p>';
            return;
        }
        coverageData = data;
        renderCoverage();
        document.getElementById('coverageUpdated').textContent =
            'Checked ' + new Date().toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'});
    } finally {
        coverageLoading = false;
    }
}

function renderCoverage() {
    if (!coverageData) return;
    const seasons = coverageData.seasons;
    const summary = [
        ['Season summaries', seasons.filter(s => s.season_rows > 0).length, 'seasons with player averages'],
        ['Individual game logs', seasons.filter(s => s.total_rows > 0).length, 'seasons with game records'],
        ['Matching season totals', seasons.filter(s => s.status === 'complete').length, 'verified against stored summaries'],
        ['Player game records', seasons.reduce((n, s) => n + s.total_rows, 0), 'one record per player, per game'],
    ];
    document.getElementById('coverageSummary').innerHTML = summary.map(([label, value, note]) => `
        <div class="stat-card"><div class="stat-label">${label}</div>
        <div class="stat-value">${NBA.count(value)}</div><div class="stat-note">${note}</div></div>`).join('');
    const filter = document.getElementById('coverageFilter').value;
    const visible = [...seasons].sort((a, b) => b.season - a.season).filter(s =>
        filter === 'all' || (filter === 'available' ? s.total_rows > 0 : s.status !== 'complete'));
    const active = coverageData.active_tasks || {};
    const labels = {
        complete: 'Matches season totals', partial: 'Some games missing',
        empty: 'Game logs not collected', mismatch: 'Review record counts',
        unverified: 'No season reference', running: 'Collecting game logs',
    };
    document.getElementById('playerStatsBody').innerHTML = visible.length
        ? '<div class="coverage-grid">' + visible.map(s => {
            const running = Object.prototype.hasOwnProperty.call(active, s.season);
            const status = running ? 'running' : s.status;
            const pct = s.expected_rows > 0 ? Math.min(100, Math.round(s.matched_rows / s.expected_rows * 100)) : 0;
            let hint = s.status === 'complete'
                ? 'Game counts match the stored season summary for every player.'
                : s.status === 'empty'
                ? 'Season averages can be available before individual games are collected.'
                : s.status === 'unverified'
                ? 'Collect season summaries before checking game coverage.'
                : s.status === 'mismatch'
                ? `${NBA.count(s.extra_rows)} extra and ${NBA.count(s.missing_rows)} missing records against stored summaries.`
                : `${NBA.count(s.missing_rows)} game records missing across ${NBA.count(s.players_needing_update)} players.`;
            if (running) hint = String(active[s.season] || 'Collection is in progress.');
            let actions;
            if (running) {
                actions = '<button class="btn btn-outline-secondary btn-sm" disabled>Collecting…</button>';
            } else {
                actions = s.missing_players > 0 && s.total_rows > 0
                    ? `<button class="btn btn-outline-secondary btn-sm" onclick="collectPlayerStats(${s.season}, true)">Retry missing players</button>` : '';
                actions += `<button class="btn btn-outline-secondary btn-sm" onclick="collectPlayerStats(${s.season}, false)" aria-label="${s.total_rows ? 'Refresh' : 'Collect'} game logs for ${seasonLabel(s.season)}">${s.total_rows ? 'Refresh game logs' : 'Collect game logs'} <i class="bi bi-arrow-down ms-1" aria-hidden="true"></i></button>`;
            }
            return `<article class="season-card" data-season="${s.season}">
                <header class="season-card__header"><h3>${seasonLabel(s.season)}</h3>
                    <span class="coverage-status ${status}">${labels[status] || 'Review coverage'}</span></header>
                <div class="coverage-details"><dl>
                    <div class="coverage-row"><dt>Season summaries</dt><dd class="${s.season_rows ? 'available' : ''}">${s.season_rows ? NBA.count(s.expected_players) + ' players' : 'Not collected'}</dd></div>
                    <div class="coverage-row"><dt>${s.expected_players ? 'Reference players with logs' : 'Players with game logs'}</dt><dd>${s.expected_players ? NBA.count(s.collected_players) + ' / ' + NBA.count(s.expected_players) : NBA.count(s.logged_players)}</dd></div>
                    <div class="coverage-row"><dt>Individual game records</dt><dd>${NBA.count(s.total_rows)}</dd></div>
                </dl><div class="coverage-progress" role="progressbar" aria-label="Game records matched to season summaries" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}">
                    <span style="width:${pct}%"></span></div><p class="coverage-hint">${NBA.escape(hint)}</p></div>
                <div class="season-actions">${actions}</div></article>`;
        }).join('') + '</div>' : '<p class="empty-state">No seasons match this filter.</p>';
}

async function collectPlayerStats(season, retry) {
    const label = seasonLabel(season);
    const action = retry ? 'retry missing players' : 'collect individual game logs';
    if (!confirm(`${action} for ${label}? This may take a while.`)) return;

    const res = await fetch('/nba/admin/api/player-stats/collect', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({season, retry})
    });
    const data = await res.json();
    if (!res.ok || data.error) { alert(data.error || 'Collection could not start.'); return; }
    updateLog({['game_stats_' + season]: {status: data.status, message: data.message || `Started for ${label}`}});
    loadPlayerStatsCoverage();
}
