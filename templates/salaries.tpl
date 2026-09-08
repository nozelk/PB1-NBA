% rebase('base.tpl', title='Salaries', page='salaries')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>Salary Analysis</h2>
    </div>

    <!-- Tabs -->
    <div class="nav-tabs-nba mb-4">
        <button class="tab-btn active" data-tab="payroll">Payroll vs Wins</button>
        <button class="tab-btn" data-tab="value">Best Value Players</button>
    </div>

    <!-- Filters -->
    <div class="d-flex gap-3 mb-4">
        <select id="salSeason" class="form-select" style="width:auto;"></select>
    </div>

    <div id="salContent">
        <div class="skeleton skeleton-card" style="height:400px;"></div>
    </div>
</div>

<script>
function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
let scatterChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    const seasons = await NBA.fetchJSON('/api/seasons');
    const sel = document.getElementById('salSeason');
    if (seasons) {
        seasons.forEach((s, i) => {
            const opt = document.createElement('option');
            opt.value = s; opt.text = seasonLabel(s);
            if (i === 0) opt.selected = true;
            sel.appendChild(opt);
        });
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadSalTab();
        });
    });

    sel.addEventListener('change', loadSalTab);
    loadSalTab();
});

function activeTab() { return document.querySelector('.tab-btn.active')?.dataset.tab || 'payroll'; }

async function loadSalTab() {
    const tab = activeTab();
    const season = document.getElementById('salSeason').value;
    const el = document.getElementById('salContent');
    NBA.showLoading(el);

    if (tab === 'payroll') {
        const data = await NBA.fetchJSON(`/api/salaries/payroll-vs-wins?season=${season}`);
        if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No salary data for this season.</p>'; return; }

        el.innerHTML = `
            <div class="chart-container mb-4"><canvas id="payrollChart" height="400"></canvas></div>
            <div style="overflow-x:auto;"><table class="table-dark-custom">
                <thead><tr><th>Team</th><th>Payroll</th><th>Wins</th><th>$/Win</th></tr></thead>
                <tbody>${data.map(t => `<tr>
                    <td><a href="/team/${t.team_id}" style="color:var(--text-primary);">${t.full_name || t.abbreviation}</a></td>
                    <td class="num">$${(t.total_payroll||0).toLocaleString('en-US')}</td>
                    <td class="num">${t.wins || 0}</td>
                    <td class="num">$${t.wins ? Math.round(t.total_payroll / t.wins).toLocaleString('en-US') : '-'}</td>
                </tr>`).join('')}</tbody></table></div>`;

        if (scatterChart) scatterChart.destroy();
        const ctx = document.getElementById('payrollChart').getContext('2d');
        scatterChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Teams',
                    data: data.map(t => ({ x: t.total_payroll / 1e6, y: t.wins || 0 })),
                    backgroundColor: NBA.CYAN + '80',
                    borderColor: NBA.CYAN,
                    pointRadius: 8,
                    pointHoverRadius: 12
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Payroll vs Wins', color: '#e8e8f0' },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const t = data[ctx.dataIndex];
                                return `${t.full_name || t.abbreviation}: $${(t.total_payroll/1e6).toFixed(1)}M, ${t.wins}W`;
                            }
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: 'Payroll ($M)', color: '#8888aa' }, grid: { color: 'rgba(42,42,68,0.3)' }, ticks: { callback: v => '$'+v+'M' } },
                    y: { title: { display: true, text: 'Wins', color: '#8888aa' }, grid: { color: 'rgba(42,42,68,0.3)' }, beginAtZero: true }
                }
            }
        });
    } else {
        const data = await NBA.fetchJSON(`/api/salaries/best-value?season=${season}&limit=30`);
        if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No value data for this season.</p>'; return; }

        el.innerHTML = `
            <p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:1rem;">Best GameScore per $1M salary</p>
            <div style="overflow-x:auto;"><table class="table-dark-custom">
                <thead><tr><th>#</th><th>Player</th><th>Team</th><th>Salary</th><th>PPG</th><th>GmSc</th><th>Value</th></tr></thead>
                <tbody>${data.map((p, i) => `<tr style="cursor:pointer;" onclick="location.href='/player/${p.player_id}'">
                    <td class="num">${i+1}</td>
                    <td><strong>${p.full_name || p.player_name}</strong></td>
                    <td>${p.team_abbreviation || '-'}</td>
                    <td class="num">$${(p.salary||0).toLocaleString('en-US')}</td>
                    <td class="num">${NBA.fmt(p.ppg)}</td>
                    <td class="num">${NBA.fmt(p.game_score)}</td>
                    <td class="num" style="color:var(--accent-green);">${NBA.fmt(p.value_score, 2)}</td>
                </tr>`).join('')}</tbody></table></div>`;
    }
}
</script>
