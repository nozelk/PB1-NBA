from bottle import Bottle, request, template, static_file, response
from database import query_db
import json
import re

team_app = Bottle()


def json_response(data):
    response.content_type = 'application/json'
    return json.dumps(data, default=str)


def _year_param(default=2025):
    s = request.query.get('season', '')
    if s:
        try:
            return int(s)
        except ValueError:
            return default
    return default


# ============================================================
# PAGES
# ============================================================
@team_app.route('/')
def teams_list():
    return template('teams_list')


@team_app.route('/<team_id:int>')
def team_profile(team_id):
    return template('team_profile', team_id=team_id)


# ============================================================
# API ENDPOINTS
# ============================================================
@team_app.route('/api/all')
def api_all_teams():
    data = query_db("""
        SELECT t.id as team_id, t.full_name, t.abbreviation, t.nickname, t.city,
               t.conference, t.division, t.year_founded, t.arena
        FROM teams t
        ORDER BY t.conference, t.full_name
    """)
    return json_response(data)


@team_app.route('/api/<team_id:int>')
def api_team_detail(team_id):
    team = query_db("""
        SELECT id as team_id, full_name, abbreviation, nickname, city, state,
               conference, division, year_founded, arena, owner, gm
        FROM teams WHERE id = ?
    """, (team_id,), one=True)
    if not team:
        response.status = 404
        return json_response({'error': 'Team not found'})
    return json_response(team)


@team_app.route('/api/<team_id:int>/seasons')
def api_team_seasons(team_id):
    data = query_db("""
        SELECT ts.season_year as season,
               ts.wins, ts.losses, ts.win_pct,
               COALESCE(ts.conf_rank,
                   (SELECT COUNT(*) + 1
                    FROM team_season_stats ts2
                    JOIN teams t2 ON ts2.team_id = t2.id
                    WHERE ts2.season_year = ts.season_year
                      AND CASE WHEN t2.conference IN ('Eastern','East') THEN 'East' ELSE 'West' END
                        = CASE WHEN t_main.conference IN ('Eastern','East') THEN 'East' ELSE 'West' END
                      AND ts2.win_pct > ts.win_pct)
               ) as conf_rank,
               ts.playoff_result,
               ROUND(CAST(ts.pts AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as ppg,
               ROUND(CAST(ts.reb AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as rpg,
               ROUND(CAST(ts.ast AS REAL) / NULLIF(ts.wins + ts.losses, 0), 1) as apg,
               ts.fg_pct, ts.fg3_pct, ts.ft_pct,
               ts.off_rating, ts.def_rating, ts.net_rating
        FROM team_season_stats ts
        JOIN teams t_main ON ts.team_id = t_main.id
        WHERE ts.team_id = ?
        ORDER BY ts.season_year DESC
    """, (team_id,))
    return json_response(data)


@team_app.route('/api/<team_id:int>/games')
def api_team_games(team_id):
    year = _year_param()
    data = query_db("""
        SELECT g.game_date, g.matchup, g.wl, g.pts,
               COALESCE(away_g.pts, g.opp_pts, 0) as opp_pts,
               g.reb, g.ast, g.stl, g.blk, g.fg_pct, g.fg3_pct,
               g.plus_minus
        FROM games g
        LEFT JOIN games away_g ON away_g.game_id = g.game_id
                              AND away_g.team_id = g.opponent_id
        WHERE g.team_id = ? AND g.season_year = ?
        ORDER BY date_iso(g.game_date) DESC
    """, (team_id, year))
    return json_response(data)


@team_app.route('/api/<team_id:int>/roster')
def api_team_roster(team_id):
    year = _year_param()
    data = query_db("""
        SELECT p.id as player_id, p.display_name as full_name,
               p.position, r.jersey_num as jersey_number
        FROM rosters r
        JOIN players p ON r.player_id = p.id
        WHERE r.team_id = ? AND r.season_year = ?
        ORDER BY p.display_name
    """, (team_id, year))
    return json_response(data)


@team_app.route('/api/<team_id:int>/h2h')
def api_team_h2h(team_id):
    opp_id = request.query.get('opponent_id', '0')
    try:
        opp_id = int(opp_id)
    except ValueError:
        return json_response({'error': 'Invalid opponent_id'})
    if not opp_id:
        return json_response({'error': 'Missing opponent_id'})

    totals = query_db("""
        SELECT COUNT(*) as total_games,
               SUM(CASE WHEN wl = 'W' THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN wl = 'L' THEN 1 ELSE 0 END) as losses,
               ROUND(AVG(pts), 1) as avg_pts
        FROM games WHERE team_id = ? AND opponent_id = ?
    """, (team_id, opp_id), one=True)

    return json_response(totals or {'total_games': 0, 'wins': 0, 'losses': 0, 'avg_pts': 0})


@team_app.route('/api/<team_id:int>/monthly')
def api_team_monthly(team_id):
    year = _year_param()
    data = query_db("""
        SELECT SUBSTR(game_date, 6, 2) as month,
               SUM(CASE WHEN wl = 'W' THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN wl = 'L' THEN 1 ELSE 0 END) as losses,
               ROUND(AVG(pts), 1) as avg_pts,
               COUNT(*) as games
        FROM games
        WHERE team_id = ? AND season_year = ?
        GROUP BY month ORDER BY month
    """, (team_id, year))
    return json_response(data)


@team_app.route('/api/<team_id:int>/streaks')
def api_team_streaks(team_id):
    year = _year_param()

    games = query_db("""
        SELECT g.game_date, g.wl, g.pts,
               COALESCE(away_g.pts, g.opp_pts, 0) as opp_pts,
               g.matchup, g.opponent_id,
               t_opp.abbreviation as opp_abbr
        FROM games g
        LEFT JOIN games away_g ON away_g.game_id = g.game_id
                              AND away_g.team_id = g.opponent_id
        LEFT JOIN teams t_opp ON g.opponent_id = t_opp.id
        WHERE g.team_id = ? AND g.season_year = ?
        ORDER BY date_iso(g.game_date)
    """, (team_id, year))

    if not games:
        return json_response({
            'longest_win_streak': 0, 'longest_loss_streak': 0,
            'current_streak': '-', 'streaks': []
        })

    # Calculate streaks
    max_w = max_l = cur = 0
    cur_type = games[0]['wl'] if games else ''
    cur = 1
    max_w = 1 if cur_type == 'W' else 0
    max_l = 1 if cur_type == 'L' else 0

    for i in range(1, len(games)):
        if games[i]['wl'] == cur_type:
            cur += 1
        else:
            cur_type = games[i]['wl']
            cur = 1
        if cur_type == 'W' and cur > max_w:
            max_w = cur
        if cur_type == 'L' and cur > max_l:
            max_l = cur

    current_str = f"{cur_type}{cur}" if games else '-'

    return json_response({
        'longest_win_streak': max_w,
        'longest_loss_streak': max_l,
        'current_streak': current_str,
        'streaks': [{
            'game_date': g['game_date'],
            'wl': g['wl'],
            'pts': g['pts'],
            'opp_pts': g['opp_pts'],
            'opp_abbr': g['opp_abbr'],
            'opponent_id': g['opponent_id'],
            'matchup': g['matchup']
        } for g in games]
    })


@team_app.route('/api/<team_id:int>/leaders')
def api_team_leaders(team_id):
    year = _year_param()
    # Get top players from this team for the given season
    scorers = query_db("""
        SELECT p.id as player_id, p.display_name as full_name,
               ROUND(CAST(ps.pts AS REAL)/NULLIF(ps.gp,0),1) as ppg,
               ps.gp
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        WHERE ps.team_id = ? AND ps.season_year = ?
        ORDER BY ppg DESC LIMIT 5
    """, (team_id, year))
    rebounders = query_db("""
        SELECT p.id as player_id, p.display_name as full_name,
               ROUND(CAST(ps.reb AS REAL)/NULLIF(ps.gp,0),1) as rpg,
               ps.gp
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        WHERE ps.team_id = ? AND ps.season_year = ?
        ORDER BY rpg DESC LIMIT 5
    """, (team_id, year))
    assisters = query_db("""
        SELECT p.id as player_id, p.display_name as full_name,
               ROUND(CAST(ps.ast AS REAL)/NULLIF(ps.gp,0),1) as apg,
               ps.gp
        FROM player_season_stats ps
        JOIN players p ON ps.player_id = p.id
        WHERE ps.team_id = ? AND ps.season_year = ?
        ORDER BY apg DESC LIMIT 5
    """, (team_id, year))
    return json_response({
        'scorers': scorers,
        'rebounders': rebounders,
        'assisters': assisters
    })






# Logo shortcut
@team_app.route('/logo/<team>')
def team_logo(team):
    clean = re.sub(r'[^a-zA-Z0-9_]', '', team.replace(" ", "_"))
    return static_file(f"{clean}.png", root='./static/images/logos/')