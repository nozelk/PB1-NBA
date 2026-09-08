from bottle import Bottle, run, static_file, template, TEMPLATE_PATH, response, request
import json
from teams import team_app
from players import player_app
from coaches import coach_app
from games import games_app

from database import query_db, init_db
from per_utils import compute_per_for_season

TEMPLATE_PATH.append('./templates')

app = Bottle()
app.mount("/team", team_app)
app.mount("/player", player_app)
app.mount("/coach", coach_app)
app.mount("/games", games_app)



def json_response(data):
    response.content_type = 'application/json'
    return json.dumps(data, default=str)


def _latest_season(table='team_season_stats'):
    r = query_db(f"SELECT MAX(season_year) as y FROM {table}", one=True)
    return r['y'] if r and r['y'] else 2024


def _get_season_param():
    s = request.query.get('season', '')
    if s:
        try:
            return int(s)
        except ValueError:
            # Handle "2023-24" format
            return int(s.split('-')[0]) + 1 if '-' in s else 2024
    return None


# ============================================================
# STATIC FILES
# ============================================================
@app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./static')


# ============================================================
# PAGES
# ============================================================
@app.route('/')
def home():
    return template('home')


@app.route('/leaders')
def leaders_page():
    return template('leaders')


@app.route('/compare')
def compare_page():
    return template('compare')




# ============================================================
# DASHBOARD API
# ============================================================
@app.route('/api/dashboard')
def api_dashboard():
    year = _get_season_param() or _latest_season()

    # Overview counts
    total_teams = query_db("SELECT COUNT(*) as c FROM teams", one=True)['c']
    total_players = query_db("SELECT COUNT(*) as c FROM players", one=True)['c']
    total_games = query_db("SELECT COUNT(*) as c FROM games", one=True)['c']
    total_seasons = query_db("SELECT COUNT(DISTINCT season_year) as c FROM team_season_stats", one=True)['c']
    total_coaches = query_db("SELECT COUNT(*) as c FROM coaches", one=True)['c']

    # Top 25 scorers
    top_scorers = query_db("""
        SELECT p.display_name as full_name, p.id as player_id,
               t.abbreviation,
               ROUND(CAST(ps.pts AS REAL) / NULLIF(ps.gp, 0), 1) as ppg
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.season_year = ? AND ps.gp > 20
        ORDER BY ppg DESC LIMIT 25
    """, (year,))

    # Top 25 assists
    top_assists = query_db("""
        SELECT p.display_name as full_name, p.id as player_id,
               t.abbreviation,
               ROUND(CAST(ps.ast AS REAL) / NULLIF(ps.gp, 0), 1) as apg
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.season_year = ? AND ps.gp > 20
        ORDER BY apg DESC LIMIT 25
    """, (year,))

    # Top 25 rebounders
    top_rebounds = query_db("""
        SELECT p.display_name as full_name, p.id as player_id,
               t.abbreviation,
               ROUND(CAST(ps.reb AS REAL) / NULLIF(ps.gp, 0), 1) as rpg
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.season_year = ? AND ps.gp > 20
        ORDER BY rpg DESC LIMIT 25
    """, (year,))

    # Top 25 steals
    top_steals = query_db("""
        SELECT p.display_name as full_name, p.id as player_id,
               t.abbreviation,
               ROUND(CAST(ps.stl AS REAL) / NULLIF(ps.gp, 0), 1) as spg
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.season_year = ? AND ps.gp > 20
        ORDER BY spg DESC LIMIT 25
    """, (year,))

    # Standings (combined with conference field)
    standings = query_db("""
        SELECT t.id as team_id, t.full_name, t.abbreviation,
               CASE WHEN t.conference IN ('Eastern','East') THEN 'East' ELSE 'West' END as conference,
               t.division,
               ts.wins, ts.losses, ts.win_pct,
               COALESCE(ts.conf_rank,
                   ROW_NUMBER() OVER (
                       PARTITION BY CASE WHEN t.conference IN ('Eastern','East') THEN 'East' ELSE 'West' END
                       ORDER BY ts.win_pct DESC
                   )
               ) as conf_rank
        FROM team_season_stats ts
        JOIN teams t ON ts.team_id = t.id
        WHERE ts.season_year = ?
        ORDER BY ts.win_pct DESC
    """, (year,))

    # League trends
    league_trends = query_db("""
        SELECT season_year as season,
               ROUND(AVG(CAST(pts AS REAL) / NULLIF(wins + losses, 0)), 1) as avg_ppg,
               ROUND(AVG(fg3_pct), 4) as avg_fg3_pct
        FROM team_season_stats
        GROUP BY season_year
        ORDER BY season_year
    """)

    # Division leaders (top team per division)
    div_rows = query_db("""
        SELECT t.id as team_id, t.full_name, t.abbreviation,
               CASE WHEN t.conference IN ('Eastern','East') THEN 'East' ELSE 'West' END as conference,
               t.division, t.logo_path,
               ts.wins, ts.losses, ts.win_pct,
               ROUND(CAST(ts.pts AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as ppg
        FROM team_season_stats ts
        JOIN teams t ON ts.team_id = t.id
        WHERE ts.season_year = ?
        ORDER BY t.division, ts.wins DESC
    """, (year,))
    seen_divs = {}
    division_leaders = []
    for row in div_rows:
        d = row['division']
        if d not in seen_divs:
            seen_divs[d] = True
            division_leaders.append(dict(row))

    return json_response({
        'season': year,
        'total_teams': total_teams,
        'total_players': total_players,
        'total_games': total_games,
        'total_seasons': total_seasons,
        'total_coaches': total_coaches,
        'top_scorers': top_scorers,
        'top_assists': top_assists,
        'top_rebounds': top_rebounds,
        'top_steals': top_steals,
        'standings': standings,
        'league_trends': league_trends,
        'division_leaders': division_leaders
    })


# ============================================================
# LEADERS API
# ============================================================
@app.route('/api/leaders')
def api_leaders():
    year = _get_season_param() or _latest_season('player_season_stats')
    category = request.query.get('category', 'ppg')
    limit = int(request.query.get('limit', 25))
    min_gp = int(request.query.get('min_gp', 20))

    # Map category names to SQL expressions
    cat_map = {
        'ppg': "ROUND(CAST(ps.pts AS REAL) / NULLIF(ps.gp, 0), 1)",
        'rpg': "ROUND(CAST(ps.reb AS REAL) / NULLIF(ps.gp, 0), 1)",
        'apg': "ROUND(CAST(ps.ast AS REAL) / NULLIF(ps.gp, 0), 1)",
        'spg': "ROUND(CAST(ps.stl AS REAL) / NULLIF(ps.gp, 0), 1)",
        'bpg': "ROUND(CAST(ps.blk AS REAL) / NULLIF(ps.gp, 0), 1)",
        'fg_pct': "ps.fg_pct",
        'fg3_pct': "ps.fg3_pct",
        'ft_pct': "ps.ft_pct",
    }
    expr = cat_map.get(category, cat_map['ppg'])

    data = query_db(f"""
        SELECT p.display_name as full_name, p.id as player_id,
               t.abbreviation as team_abbreviation,
               ps.gp,
               ROUND(CAST(ps.pts AS REAL) / NULLIF(ps.gp, 0), 1) as ppg,
               ROUND(CAST(ps.reb AS REAL) / NULLIF(ps.gp, 0), 1) as rpg,
               ROUND(CAST(ps.ast AS REAL) / NULLIF(ps.gp, 0), 1) as apg,
               ROUND(CAST(ps.stl AS REAL) / NULLIF(ps.gp, 0), 1) as spg,
               ROUND(CAST(ps.blk AS REAL) / NULLIF(ps.gp, 0), 1) as bpg,
               ps.fg_pct, ps.fg3_pct, ps.ft_pct,
               {expr} as sort_val
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.season_year = ? AND ps.gp >= ?
        ORDER BY sort_val DESC
        LIMIT ?
    """, (year, min_gp, limit))

    return json_response(data)


# ============================================================
# COMPARE API
# ============================================================
@app.route('/api/compare/players')
def api_compare_players():
    id1 = request.query.get('id1', '')
    id2 = request.query.get('id2', '')
    if not id1 or not id2:
        return json_response({'error': 'Need id1 and id2'})

    def get_career(pid):
        return query_db("""
            SELECT p.display_name as full_name, p.id as player_id, p.position,
                   ROUND(CAST(SUM(ps.pts) AS REAL) / NULLIF(SUM(ps.gp), 0), 1) as ppg,
                   ROUND(CAST(SUM(ps.reb) AS REAL) / NULLIF(SUM(ps.gp), 0), 1) as rpg,
                   ROUND(CAST(SUM(ps.ast) AS REAL) / NULLIF(SUM(ps.gp), 0), 1) as apg,
                   ROUND(CAST(SUM(ps.stl) AS REAL) / NULLIF(SUM(ps.gp), 0), 1) as spg,
                   ROUND(CAST(SUM(ps.blk) AS REAL) / NULLIF(SUM(ps.gp), 0), 1) as bpg,
                   ROUND(SUM(ps.fgm)*1.0 / NULLIF(SUM(ps.fga), 0), 3) as fg_pct,
                   ROUND(SUM(ps.fg3m)*1.0 / NULLIF(SUM(ps.fg3a), 0), 3) as fg3_pct,
                   ROUND(SUM(ps.ftm)*1.0 / NULLIF(SUM(ps.fta), 0), 3) as ft_pct,
                   ROUND(CAST(SUM(ps.pts) AS REAL) / NULLIF(2*(SUM(ps.fga)+0.44*SUM(ps.fta)), 0), 3) as ts_pct,
                   ROUND((SUM(ps.pts) + 0.4*SUM(ps.fgm) - 0.7*SUM(ps.fga)
                       - 0.4*(SUM(ps.fta)-SUM(ps.ftm)) + 0.7*SUM(ps.oreb)
                       + 0.3*SUM(ps.dreb) + SUM(ps.stl) + 0.7*SUM(ps.ast)
                       + 0.7*SUM(ps.blk) - 0.4*SUM(ps.pf) - SUM(ps.tov))
                       / NULLIF(SUM(ps.gp), 0), 1) as game_score
            FROM player_season_stats ps
            JOIN players p ON ps.player_id = p.id
            WHERE ps.player_id = ?
        """, (int(pid),), one=True)

    p1 = get_career(id1)
    p2 = get_career(id2)
    return json_response({'player1': p1, 'player2': p2})


@app.route('/api/compare/teams')
def api_compare_teams():
    id1 = request.query.get('id1', '')
    id2 = request.query.get('id2', '')
    year = _get_season_param() or _latest_season()

    def get_team(tid):
        return query_db("""
            SELECT t.id as team_id, t.full_name, t.abbreviation,
                   ts.wins, ts.losses, ts.win_pct,
                   ROUND(CAST(ts.pts AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as ppg,
                   ROUND(CAST(ts.reb AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as rpg,
                   ROUND(CAST(ts.ast AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as apg,
                   ts.fg_pct, ts.fg3_pct, ts.ft_pct
            FROM team_season_stats ts
            JOIN teams t ON ts.team_id = t.id
            WHERE ts.team_id = ? AND ts.season_year = ?
        """, (int(tid), year), one=True)

    t1 = get_team(id1) if id1 else None
    t2 = get_team(id2) if id2 else None
    return json_response({'team1': t1, 'team2': t2})


# ============================================================
# SALARY API
# ============================================================




# ============================================================
# SEARCH API
# ============================================================
@app.route('/api/search')
def api_search():
    q = request.query.get('q', '').strip()
    if len(q) < 2:
        return json_response({'players': [], 'teams': []})

    players = query_db("""
        SELECT id as player_id, display_name as full_name, position
        FROM players WHERE display_name LIKE ? LIMIT 10
    """, (f"%{q}%",))

    teams = query_db("""
        SELECT id as team_id, full_name, abbreviation
        FROM teams WHERE full_name LIKE ? OR abbreviation LIKE ? LIMIT 10
    """, (f"%{q}%", f"%{q}%"))

    return json_response({'players': players, 'teams': teams})


# ============================================================
# SEASONS LIST
# ============================================================
@app.route('/api/seasons')
def api_seasons():
    seasons = query_db("""
        SELECT DISTINCT season_year FROM team_season_stats ORDER BY season_year DESC
    """)
    return json_response([s['season_year'] for s in seasons])


# ============================================================
# BEST PERFORMANCES API  (daily / weekly / monthly / season)
# ============================================================
@app.route('/api/best-performances')
def api_best_performances():
    """
    Top individual game performances ranked by Game Score (Hollinger).
    GmSc = PTS + 0.4*FGM - 0.7*FGA - 0.4*(FTA-FTM)
         + 0.7*OREB + 0.3*DREB + STL + 0.7*AST + 0.7*BLK - 0.4*PF - TOV
    """
    period = request.query.get('period', 'week')   # day / week / month / season
    limit = int(request.query.get('limit', 10))
    year = _get_season_param() or _latest_season('player_game_stats')

    # Build date filter  — dates stored as "Feb 03, 2026" so use date_iso()
    # "day"   = latest game date
    # "week"  = same calendar week (Mon–Sun) as latest game date
    # "month" = same calendar month as latest game date
    if period == 'day':
        date_filter = "AND date_iso(pgs.game_date) = (SELECT MAX(date_iso(game_date)) FROM player_game_stats WHERE season_year = ?)"
        args_extra = [year]
    elif period == 'week':
        date_filter = ("AND strftime('%Y-%W', date_iso(pgs.game_date)) = "
                       "strftime('%Y-%W', (SELECT MAX(date_iso(game_date)) FROM player_game_stats WHERE season_year = ?))")
        args_extra = [year]
    elif period == 'month':
        date_filter = ("AND strftime('%Y-%m', date_iso(pgs.game_date)) = "
                       "strftime('%Y-%m', (SELECT MAX(date_iso(game_date)) FROM player_game_stats WHERE season_year = ?))")
        args_extra = [year]
    else:
        date_filter = ""
        args_extra = []

    data = query_db(f"""
        SELECT p.id as player_id, p.display_name as full_name,
               p.position, p.image_path,
               t.abbreviation as team_abbreviation,
               pgs.game_date, pgs.matchup, pgs.wl,
               pgs.pts, pgs.reb, pgs.ast, pgs.stl, pgs.blk, pgs.tov,
               pgs.fgm, pgs.fga, pgs.fg_pct, pgs.fg3m, pgs.fg3a, pgs.fg3_pct,
               pgs.ftm, pgs.fta, pgs.plus_minus, pgs.min,
               pgs.game_score
        FROM player_game_stats pgs
        JOIN players p ON pgs.player_id = p.id
        LEFT JOIN teams t ON pgs.team_id = t.id
        WHERE pgs.season_year = ? {date_filter}
          AND pgs.min > 10
        ORDER BY pgs.game_score DESC
        LIMIT ?
    """, tuple([year] + args_extra + [limit]))

    return json_response(data)


# ============================================================
# PLAYER OF THE WEEK / MONTH API
# ============================================================
@app.route('/api/player-of-the-week')
def api_player_of_the_week():
    """Latest Player of the Week/Month + Rookie/Defensive for each conference."""
    year = _get_season_param() or _latest_season('player_season_stats')

    def _query_award(description):
        return query_db("""
            SELECT a.id as award_id, a.player_id, p.display_name as full_name,
                   t.abbreviation as team_abbreviation, t.id as team_id,
                   CASE WHEN t.conference IN ('Eastern','East') THEN 'East' ELSE 'West' END as conference,
                   ROUND(CAST(ps.pts AS REAL) / NULLIF(ps.gp, 0), 1) as ppg,
                   ROUND(CAST(ps.reb AS REAL) / NULLIF(ps.gp, 0), 1) as rpg,
                   ROUND(CAST(ps.ast AS REAL) / NULLIF(ps.gp, 0), 1) as apg
            FROM awards a
            JOIN players p ON a.player_id = p.id
            JOIN player_season_stats ps ON ps.player_id = a.player_id AND ps.season_year = a.season_year
            JOIN teams t ON ps.team_id = t.id
            WHERE a.description = ? AND a.season_year = ?
            ORDER BY a.id DESC
        """, (description, year))

    def _pick_east_west(rows):
        east = west = None
        for r in rows:
            if r['conference'] == 'East' and not east:
                east = dict(r)
            elif r['conference'] == 'West' and not west:
                west = dict(r)
            if east and west:
                break
        return east, west

    pow_e, pow_w = _pick_east_west(_query_award('NBA Player of the Week'))
    pom_e, pom_w = _pick_east_west(_query_award('NBA Player of the Month'))
    dpom_e, dpom_w = _pick_east_west(_query_award('NBA Defensive Player of the Month'))
    rom_e, rom_w = _pick_east_west(_query_award('NBA Rookie of the Month'))

    return json_response({
        'pow_east': pow_e, 'pow_west': pow_w,
        'pom_east': pom_e, 'pom_west': pom_w,
        'dpom_east': dpom_e, 'dpom_west': dpom_w,
        'rom_east': rom_e, 'rom_west': rom_w,
    })


# ============================================================
# TOP RATED PLAYERS API  (Hollinger PER – same as Basketball Reference)
# ============================================================
@app.route('/api/top-rated')
def api_top_rated():
    """
    Player Efficiency Rating (PER) – Hollinger formula.
    Normalised so league average = 15.0.
    Minimum 30 GP and 24 MPG to qualify.
    """
    year = _get_season_param() or _latest_season('player_season_stats')
    limit = int(request.query.get('limit', 5))

    # Compute PER for all players via shared utility
    per_map = compute_per_for_season(year)
    if not per_map:
        return json_response([])

    # All player season stats for the year (for response building)
    rows = query_db("""
        SELECT ps.player_id, ps.team_id, ps.gp, ps.min,
               ps.fgm, ps.fga, ps.fg3m, ps.fg3a,
               ps.ftm, ps.fta, ps.oreb, ps.dreb, ps.reb,
               ps.ast, ps.stl, ps.blk, ps.tov, ps.pf, ps.pts,
               ps.plus_minus,
               p.display_name as full_name, p.position, p.image_path,
               t.abbreviation as team_abbreviation
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t  ON ps.team_id   = t.id
        WHERE ps.season_year = ? AND ps.gp >= 1 AND ps.min > 0
    """, (year,))
    if not rows:
        return json_response([])

    # Team win records
    team_wp = {}
    for tr in (query_db("""
        SELECT team_id,
               SUM(CASE WHEN wl='W' THEN 1 ELSE 0 END) as w,
               SUM(CASE WHEN wl='L' THEN 1 ELSE 0 END) as l
        FROM games WHERE season_year = ? AND matchup LIKE '%vs.%'
        GROUP BY team_id
    """, (year,)) or []):
        total = (tr['w'] or 0) + (tr['l'] or 0)
        if total:
            team_wp[tr['team_id']] = tr['w'] / total

    # ── filter, sort, limit  (GP≥30, MPG≥24 like BBRef) ──
    qualified = []
    for r in rows:
        pid = r['player_id']
        if pid not in per_map:
            continue
        gp = r['gp'] or 0
        _min = r['min'] or 0
        if gp >= 30 and _min / gp >= 24:
            qualified.append({**dict(r), '_per': per_map[pid]})

    qualified.sort(key=lambda x: x['_per'], reverse=True)
    qualified = qualified[:limit]

    # ── build response ──
    out = []
    for p in qualified:
        gp  = max(p['gp'], 1)
        fga = p['fga'] or 0
        fta = p['fta'] or 0
        denom = 2 * (fga + 0.44 * fta)
        out.append({
            'player_id':         p['player_id'],
            'full_name':         p['full_name'],
            'position':          p['position'],
            'image_path':        p['image_path'],
            'team_abbreviation': p['team_abbreviation'],
            'gp':                p['gp'],
            'ppg': round((p['pts'] or 0) / gp, 1),
            'rpg': round((p['reb'] or 0) / gp, 1),
            'apg': round((p['ast'] or 0) / gp, 1),
            'ts_pct':     round((p['pts'] or 0) / denom, 3) if denom else None,
            'per':        round(p['_per'], 2),
            'pm_per36':   round((p['plus_minus'] or 0) / max(p['min'] or 1, 1) * 36, 1),
            'team_win_pct': team_wp.get(p['team_id']),
        })

    return json_response(out)


# ============================================================
# RECENT / FEATURED GAMES API
# ============================================================
@app.route('/api/recent-games')
def api_recent_games():
    """Most recent games with scores, sorted by date then total points."""
    year = _get_season_param() or _latest_season('games')
    limit = int(request.query.get('limit', 10))

    data = query_db("""
        SELECT g.game_date,
               g.team_id as home_team_id,
               t.abbreviation as home_team, t.full_name as home_full_name,
               g.pts as home_pts,
               g.opponent_id as away_team_id,
               opp.abbreviation as away_team, opp.full_name as away_full_name,
               COALESCE(away_g.pts, g.opp_pts, 0) as away_pts,
               g.wl,
               (g.pts + COALESCE(away_g.pts, g.opp_pts, 0)) as total_pts
        FROM games g
        JOIN teams t ON g.team_id = t.id
        LEFT JOIN teams opp ON g.opponent_id = opp.id
        LEFT JOIN games away_g ON away_g.game_id = g.game_id
                              AND away_g.team_id = g.opponent_id
        WHERE g.season_year = ? AND g.matchup LIKE '%vs.%'
        ORDER BY date_iso(g.game_date) DESC, total_pts DESC
        LIMIT ?
    """, (year, limit))

    return json_response(data)


if __name__ == '__main__':
    init_db()
    print(f"Template paths: {TEMPLATE_PATH}")
    run(app, host='localhost', port=8080, debug=True, reloader=True)