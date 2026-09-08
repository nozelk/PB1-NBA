"""
Hollinger PER (Player Efficiency Rating) – shared utility.
League average is normalised to 15.0.
"""
from database import query_db


def compute_per_for_season(season_year):
    """
    Compute Hollinger PER for every player who played in *season_year*.
    Returns dict  {player_id: per_value}  (rounded to 2 decimals).
    """
    rows = query_db("""
        SELECT ps.player_id, ps.team_id, ps.gp, ps.min,
               ps.fgm, ps.fga, ps.fg3m, ps.fg3a,
               ps.ftm, ps.fta, ps.oreb, ps.dreb, ps.reb,
               ps.ast, ps.stl, ps.blk, ps.tov, ps.pf, ps.pts
        FROM player_season_stats ps
        WHERE ps.season_year = ? AND ps.gp >= 1 AND ps.min > 0
    """, (season_year,))
    if not rows:
        return {}

    # ── league totals ──
    _k = ['fgm', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta',
          'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk',
          'tov', 'pf', 'pts', 'min']
    lg = {k: sum(r[k] or 0 for r in rows) for k in _k}
    if lg['fgm'] == 0 or lg['ftm'] == 0 or lg['pf'] == 0 or lg['reb'] == 0:
        return {}

    # ── Hollinger constants ──
    factor  = (2 / 3) - (0.5 * (lg['ast'] / lg['fgm'])) / (2 * (lg['fgm'] / lg['ftm']))
    VOP     = lg['pts'] / (lg['fga'] - lg['oreb'] + lg['tov'] + 0.44 * lg['fta'])
    DRB_pct = (lg['reb'] - lg['oreb']) / lg['reb']

    # ── team aggregates (assist-ratio & pace) ──
    tm = {}
    for r in rows:
        tid = r['team_id']
        if tid not in tm:
            tm[tid] = {k: 0 for k in ['ast', 'fgm', 'fga', 'fta', 'oreb', 'tov', 'min']}
        tm[tid]['ast'] += r['ast'] or 0
        tm[tid]['fgm'] += r['fgm'] or 0
        tm[tid]['fga'] += r['fga'] or 0
        tm[tid]['fta'] += r['fta'] or 0
        tm[tid]['oreb'] += r['oreb'] or 0
        tm[tid]['tov'] += r['tov'] or 0
        tm[tid]['min'] += r['min'] or 0

    team_paces = {}
    for tid, ts in tm.items():
        if ts['min'] > 0:
            poss = ts['fga'] + 0.44 * ts['fta'] - ts['oreb'] + ts['tov']
            team_paces[tid] = 48 * poss / (ts['min'] / 5)
    lg_pace = sum(team_paces.values()) / len(team_paces) if team_paces else 1

    # ── uPER per player ──
    players = []
    for r in rows:
        MIN = r['min']
        if MIN <= 0:
            continue
        tid = r['team_id']
        ts  = tm.get(tid, {})
        t_ar = ts['ast'] / ts['fgm'] if ts.get('fgm') else 0

        uPER = (1 / MIN) * (
            (r['fg3m'] or 0)
            + (2 / 3) * (r['ast'] or 0)
            + (2 - factor * t_ar) * (r['fgm'] or 0)
            + (r['ftm'] or 0) * 0.5 * (1 + (1 - t_ar) + (2 / 3) * t_ar)
            - VOP * (r['tov'] or 0)
            - VOP * DRB_pct * ((r['fga'] or 0) - (r['fgm'] or 0))
            - VOP * 0.44 * (0.44 + 0.56 * DRB_pct) * ((r['fta'] or 0) - (r['ftm'] or 0))
            + VOP * (1 - DRB_pct) * ((r['reb'] or 0) - (r['oreb'] or 0))
            + VOP * DRB_pct * (r['oreb'] or 0)
            + VOP * (r['stl'] or 0)
            + VOP * DRB_pct * (r['blk'] or 0)
            - (r['pf'] or 0) * ((lg['ftm'] / lg['pf']) - 0.44 * (lg['fta'] / lg['pf']) * VOP)
        )

        t_pace = team_paces.get(tid, lg_pace)
        aPER = uPER * (lg_pace / t_pace) if t_pace > 0 else uPER
        players.append({'player_id': r['player_id'], '_aPER': aPER, '_min': MIN})

    if not players:
        return {}

    # ── normalise: league-avg PER = 15 ──
    total_min = sum(p['_min'] for p in players)
    lg_aPER   = sum(p['_aPER'] * p['_min'] for p in players) / total_min if total_min else 1

    result = {}
    for p in players:
        per = p['_aPER'] * (15 / lg_aPER) if lg_aPER else 0
        result[p['player_id']] = round(per, 2)

    return result
