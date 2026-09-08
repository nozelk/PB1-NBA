from bottle import Bottle, request, template, response
from database import query_db
import json

games_app = Bottle()


def json_response(data):
    response.content_type = 'application/json'
    return json.dumps(data, default=str)


# ============================================================
# PAGES
# ============================================================
@games_app.route('/')
def games_page():
    return template('games_list')


# ============================================================
# helpers – games table has two rows per game: "vs." (home) and "@" (away).
# opp_pts is not populated, so we self-join to get away score.
# Select only "vs." rows for deduplication, join the "@" row for away pts.
# ============================================================
_GAME_COLS = """
    g.game_date,
    g.team_id   as home_team_id,
    t.abbreviation as home_team, t.full_name as home_full_name,
    g.pts       as home_pts,
    g.opponent_id as away_team_id,
    opp.abbreviation as away_team, opp.full_name as away_full_name,
    COALESCE(away_g.pts, g.opp_pts, 0) as away_pts,
    g.season_year as season,
    g.wl
"""

_GAME_JOINS = """
    FROM games g
    JOIN teams t   ON g.team_id    = t.id
    LEFT JOIN teams opp ON g.opponent_id = opp.id
    LEFT JOIN games away_g ON away_g.game_id = g.game_id
                          AND away_g.team_id = g.opponent_id
"""


# ============================================================
# API ENDPOINTS
# ============================================================
@games_app.route('/api/list')
def api_games_list():
    year = request.query.get('season', '')
    team_id = request.query.get('team_id', '') or request.query.get('team', '')
    month = request.query.get('month', '')
    limit = int(request.query.get('limit', 100))

    where_clauses = ["g.matchup LIKE '%vs.%'"]
    args = []

    if year and year != 'all':
        where_clauses.append("g.season_year = ?")
        args.append(int(year))

    if team_id:
        where_clauses.append("(g.team_id = ? OR g.opponent_id = ?)")
        args.extend([int(team_id), int(team_id)])

    if month:
        where_clauses.append("UPPER(SUBSTR(g.game_date, 1, 3)) = UPPER(?)")
        args.append(month[:3])

    where = "WHERE " + " AND ".join(where_clauses)
    args.append(limit)

    data = query_db(f"""
        SELECT {_GAME_COLS}
        {_GAME_JOINS}
        {where}
        ORDER BY date_iso(g.game_date) DESC
        LIMIT ?
    """, tuple(args))

    return json_response(data)


@games_app.route('/api/highest-scoring')
def api_highest_scoring():
    year = request.query.get('season', None)
    team_id = request.query.get('team_id', '')
    limit = int(request.query.get('limit', 50))

    where = "WHERE g.matchup LIKE '%vs.%'"
    args = []
    if year and year != 'all':
        where += " AND g.season_year = ?"
        args.append(int(year))
    if team_id:
        where += " AND (g.team_id = ? OR g.opponent_id = ?)"
        args.extend([int(team_id), int(team_id)])
    args.append(limit)

    data = query_db(f"""
        SELECT {_GAME_COLS}, (g.pts + COALESCE(away_g.pts, g.opp_pts, 0)) as total_pts
        {_GAME_JOINS}
        {where}
        ORDER BY total_pts DESC
        LIMIT ?
    """, tuple(args))
    return json_response(data)


@games_app.route('/api/biggest-blowouts')
def api_biggest_blowouts():
    year = request.query.get('season', None)
    team_id = request.query.get('team_id', '')
    limit = int(request.query.get('limit', 50))

    where = "WHERE g.matchup LIKE '%vs.%'"
    args = []
    if year and year != 'all':
        where += " AND g.season_year = ?"
        args.append(int(year))
    if team_id:
        where += " AND (g.team_id = ? OR g.opponent_id = ?)"
        args.extend([int(team_id), int(team_id)])
    args.append(limit)

    data = query_db(f"""
        SELECT {_GAME_COLS}, ABS(g.pts - COALESCE(away_g.pts, g.opp_pts, 0)) as margin
        {_GAME_JOINS}
        {where}
        ORDER BY margin DESC
        LIMIT ?
    """, tuple(args))
    return json_response(data)


@games_app.route('/api/closest-games')
def api_closest_games():
    year = request.query.get('season', None)
    team_id = request.query.get('team_id', '')
    limit = int(request.query.get('limit', 50))

    where = "WHERE g.matchup LIKE '%vs.%' AND ABS(g.pts - COALESCE(away_g.pts, g.opp_pts, 0)) > 0"
    args = []
    if year and year != 'all':
        where += " AND g.season_year = ?"
        args.append(int(year))
    if team_id:
        where += " AND (g.team_id = ? OR g.opponent_id = ?)"
        args.extend([int(team_id), int(team_id)])
    args.append(limit)

    data = query_db(f"""
        SELECT {_GAME_COLS}, ABS(g.pts - COALESCE(away_g.pts, g.opp_pts, 0)) as margin
        {_GAME_JOINS}
        {where}
        ORDER BY margin ASC
        LIMIT ?
    """, tuple(args))
    return json_response(data)


@games_app.route('/api/top-performances')
def api_top_performances():
    year = request.query.get('season', None)
    limit = int(request.query.get('limit', 50))

    where = ""
    args = []
    if year:
        where = "WHERE pgs.season_year = ?"
        args.append(int(year))
    args.append(limit)

    data = query_db(f"""
        SELECT p.display_name as player_name, p.id as player_id,
               pgs.game_date, pgs.matchup, pgs.wl,
               pgs.pts, pgs.reb, pgs.ast, pgs.stl, pgs.blk,
               pgs.fgm, pgs.fga, pgs.fg3m, pgs.fg3a, pgs.ftm, pgs.fta,
               pgs.min,
               ROUND(pgs.pts + 0.4*pgs.fgm - 0.7*pgs.fga - 0.4*(pgs.fta - pgs.ftm)
                   + 0.7*pgs.oreb + 0.3*pgs.dreb + pgs.stl + 0.7*pgs.ast
                   + 0.7*pgs.blk - 0.4*pgs.pf - pgs.tov, 1) as game_score
        FROM player_game_stats pgs
        JOIN players p ON pgs.player_id = p.id
        {where}
        ORDER BY game_score DESC
        LIMIT ?
    """, tuple(args))
    return json_response(data)
