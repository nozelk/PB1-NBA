% rebase('base.tpl', title='Leaders', page='leaders')

<div class="page-container">
    <div class="section-header">
        <h2><span class="section-icon"></span>Season Leaders</h2>
        <select id="seasonSel" class="form-select" style="width:auto;"></select>
    </div>

    <!-- Category pills -->
    <div class="pill-group mb-4" id="catPills">
        <button class="pill active" data-cat="ppg">PPG</button>
        <button class="pill" data-cat="rpg">RPG</button>
        <button class="pill" data-cat="apg">APG</button>
        <button class="pill" data-cat="spg">SPG</button>
        <button class="pill" data-cat="bpg">BPG</button>
        <button class="pill" data-cat="fg_pct">FG%</button>
        <button class="pill" data-cat="fg3_pct">3PT%</button>
        <button class="pill" data-cat="ft_pct">FT%</button>
    </div>

    <div class="row g-4">
        <div class="col-lg-7">
            <div id="leadersTable"><div class="skeleton skeleton-card" style="height:400px;"></div></div>
        </div>
        <div class="col-lg-5">
            <div class="chart-container">
                <canvas id="leadersChart" height="350"></canvas>
            </div>
        </div>
    </div>
</div>

<script>
function seasonLabel(y) { const n=parseInt(y,10); if(isNaN(n)) return y; return n+'/'+((n+1)%100).toString().padStart(2,'0'); }
let leadersChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    const seasons = await NBA.fetchJSON('/api/seasons');
    const sel = document.getElementById('seasonSel');
    if (seasons) {
        seasons.forEach((s, i) => {
            const opt = document.createElement('option');
            opt.value = s; opt.text = seasonLabel(s);
            if (i === 0) opt.selected = true;
            sel.appendChild(opt);
        });
    }

    document.querySelectorAll('#catPills .pill').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#catPills .pill').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadLeaders();
        });
    });

    sel.addEventListener('change', loadLeaders);
    loadLeaders();
});

async function loadLeaders() {
    const season = document.getElementById('seasonSel').value;
    const cat = document.querySelector('#catPills .pill.active')?.dataset.cat || 'ppg';
    const el = document.getElementById('leadersTable');
    NBA.showLoading(el);

    const data = await NBA.fetchJSON(`/api/leaders?season=${season}&category=${cat}&limit=20`);
    if (!data || !data.length) { el.innerHTML = '<p style="color:var(--text-muted);">No data.</p>'; return; }

    const isPct = cat.includes('pct');
    el.innerHTML = `<div style="overflow-x:auto;"><table class="table-dark-custom">
        <thead><tr><th>#</th><th>Player</th><th>Team</th><th>GP</th><th>${cat.toUpperCase()}</th></tr></thead>
        <tbody>${data.map((p, i) => {
            const val = isPct ? (p[cat] ? (p[cat]*100).toFixed(1)+'%' : '-') : NBA.fmt(p[cat]);
            return `<tr style="cursor:pointer;" onclick="location.href='/player/${p.player_id}'">
                <td class="num">${i+1}</td>
                <td><strong>${p.full_name || p.player_name}</strong></td>
                <td>${p.team_abbreviation || '-'}</td>
                <td class="num">${p.gp || '-'}</td>
                <td class="num" style="color:var(--accent-cyan);font-weight:600;">${val}</td>
            </tr>`;
        }).join('')}</tbody></table></div>`;

    // Chart
    if (leadersChart) leadersChart.destroy();
    const ctx = document.getElementById('leadersChart').getContext('2d');
    const top10 = data.slice(0, 10);
    leadersChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: top10.map(p => (p.full_name || p.player_name || '').split(' ').pop()),
            datasets: [{
                label: cat.toUpperCase(),
                data: top10.map(p => isPct ? (p[cat]*100) : p[cat]),
                backgroundColor: NBA.COLORS.slice(0, 10).map(c => c + '80'),
                borderColor: NBA.COLORS.slice(0, 10),
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false }, title: { display: true, text: `Top 10 - ${cat.toUpperCase()}`, color: '#e8e8f0' } },
            scales: {
                x: { grid: { color: 'rgba(42,42,68,0.3)' }, ticks: { callback: v => isPct ? v+'%' : v } },
                y: { grid: { display: false } }
            }
        }
    });
}
</script>
