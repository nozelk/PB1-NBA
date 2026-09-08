from bottle import Bottle, request, template, static_file, response
from database import query_db
from per_utils import compute_per_for_season
import json
import re

player_app = Bottle()


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
@player_app.route('/')
def players_list():
    return template('players_list')


@player_app.route('/<player_id:int>')
def player_profile(player_id):
    return template('player_profile', player_id=player_id)


# ============================================================
# API ENDPOINTS
# ============================================================
@player_app.route('/api/all')
def api_all_players():
    q = request.query.get('q', '')
    limit = int(request.query.get('limit', 500))
    offset = int(request.query.get('offset', 0))

    where = ""
    args = []
    if q:
        where = "WHERE p.display_name LIKE ?"
        args.append(f"%{q}%")

    args.extend([limit, offset])

    data = query_db(f"""
        SELECT p.id as player_id, p.display_name as full_name,
               p.position, p.country,
               p.from_year, p.to_year, p.draft_year,
               (SELECT t.abbreviation FROM player_season_stats ps2
                JOIN teams t ON ps2.team_id = t.id
                WHERE ps2.player_id = p.id
                ORDER BY ps2.season_year DESC LIMIT 1) as team_abbreviation
        FROM players p
        {where}
        ORDER BY p.display_name
        LIMIT ? OFFSET ?
    """, tuple(args))

    return json_response(data)


@player_app.route('/api/<player_id:int>')
def api_player_detail(player_id):
    player = query_db("""
        SELECT id as player_id, display_name as full_name,
               first_name, last_name, position, height, weight,
               country, school, birthdate,
               draft_year, draft_round, draft_number,
               from_year, to_year
        FROM players WHERE id = ?
    """, (player_id,), one=True)
    if not player:
        response.status = 404
        return json_response({'error': 'Player not found'})

    # Current / latest team
    team = query_db("""
        SELECT t.id as team_id, t.abbreviation as team_abbreviation,
               t.full_name as team_name
        FROM player_season_stats ps
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.player_id = ?
        ORDER BY ps.season_year DESC LIMIT 1
    """, (player_id,), one=True)
    if team:
        player['team_id'] = team['team_id']
        player['team_abbreviation'] = team['team_abbreviation']
        player['team_name'] = team['team_name']

    return json_response(player)


@player_app.route('/api/<player_id:int>/career')
def api_player_career(player_id):
    seasons = query_db("""
        SELECT ps.season_year as season, t.abbreviation as team_abbreviation,
               ps.team_id as team_id,
               ps.gp,
               ROUND(CAST(ps.pts AS REAL) / NULLIF(ps.gp, 0), 1) as ppg,
               ROUND(CAST(ps.reb AS REAL) / NULLIF(ps.gp, 0), 1) as rpg,
               ROUND(CAST(ps.ast AS REAL) / NULLIF(ps.gp, 0), 1) as apg,
               ROUND(CAST(ps.stl AS REAL) / NULLIF(ps.gp, 0), 1) as spg,
               ROUND(CAST(ps.blk AS REAL) / NULLIF(ps.gp, 0), 1) as bpg,
               ps.fg_pct, ps.fg3_pct, ps.ft_pct,
               ROUND(CAST(ps.pts AS REAL) / NULLIF(2*(ps.fga + 0.44*ps.fta), 0), 3) as ts_pct,
               ROUND((ps.fgm + 0.5*ps.fg3m) / NULLIF(ps.fga, 0), 3) as efg_pct,
               ROUND((ps.pts + 0.4*ps.fgm - 0.7*ps.fga - 0.4*(ps.fta-ps.ftm)
                   + 0.7*ps.oreb + 0.3*ps.dreb + ps.stl + 0.7*ps.ast
                   + 0.7*ps.blk - 0.4*ps.pf - ps.tov) / NULLIF(ps.gp, 0), 1) as game_score
        FROM player_season_stats ps
        JOIN teams t ON ps.team_id = t.id
        WHERE ps.player_id = ?
        ORDER BY ps.season_year DESC
    """, (player_id,))

    # Career averages
    career = query_db("""
        SELECT ROUND(CAST(SUM(pts) AS REAL) / NULLIF(SUM(gp), 0), 1) as ppg,
               ROUND(CAST(SUM(reb) AS REAL) / NULLIF(SUM(gp), 0), 1) as rpg,
               ROUND(CAST(SUM(ast) AS REAL) / NULLIF(SUM(gp), 0), 1) as apg,
               ROUND(CAST(SUM(stl) AS REAL) / NULLIF(SUM(gp), 0), 1) as spg,
               ROUND(CAST(SUM(blk) AS REAL) / NULLIF(SUM(gp), 0), 1) as bpg,
               ROUND(CAST(SUM(pts) AS REAL) / NULLIF(2*(SUM(fga)+0.44*SUM(fta)), 0), 3) as ts_pct,
               ROUND((SUM(pts) + 0.4*SUM(fgm) - 0.7*SUM(fga)
                   - 0.4*(SUM(fta)-SUM(ftm)) + 0.7*SUM(oreb) + 0.3*SUM(dreb)
                   + SUM(stl) + 0.7*SUM(ast) + 0.7*SUM(blk)
                   - 0.4*SUM(pf) - SUM(tov)) / NULLIF(SUM(gp), 0), 1) as game_score
        FROM player_season_stats WHERE player_id = ?
    """, (player_id,), one=True)

    # Compute PER for each season
    per_cache = {}
    for s in seasons:
        yr = s['season']
        if yr not in per_cache:
            per_cache[yr] = compute_per_for_season(yr)
        s['per'] = per_cache[yr].get(player_id)

    # Latest-season PER for career summary
    if seasons:
        career['per'] = seasons[0].get('per')

    return json_response({'seasons': seasons, 'career_averages': career})










# Image shortcut
@player_app.route('/image/<player>')
def player_image(player):
    clean = re.sub(r'[^a-zA-Z0-9_]', '', player.replace(" ", "_"))
    return static_file(f"{clean}.png", root='./static/images/players/')