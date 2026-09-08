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


















# Logo shortcut
@team_app.route('/logo/<team>')
def team_logo(team):
    clean = re.sub(r'[^a-zA-Z0-9_]', '', team.replace(" ", "_"))
    return static_file(f"{clean}.png", root='./static/images/logos/')