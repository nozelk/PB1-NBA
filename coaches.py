from bottle import Bottle, request, template, response
from database import query_db
import json

coach_app = Bottle()


def json_response(data):
    response.content_type = 'application/json'
    return json.dumps(data, default=str)


# ============================================================
# PAGES
# ============================================================
@coach_app.route('/')
def coaches_list():
    return template('coaches_list')


@coach_app.route('/<coach_id:int>')
def coach_profile(coach_id):
    return template('coach_profile', coach_id=coach_id)


# ============================================================
# API ENDPOINTS
# ============================================================
@coach_app.route('/api/all')
def api_all_coaches():
    data = query_db("""
        SELECT c.id as coach_id, c.name as coach_name,
               SUM(cs.wins) as total_wins,
               SUM(cs.losses) as total_losses,
               ROUND(CAST(SUM(cs.wins) AS REAL) /
                   NULLIF(SUM(cs.wins) + SUM(cs.losses), 0), 3) as win_pct,
               COUNT(DISTINCT cs.team_id) as teams_coached,
               COUNT(DISTINCT cs.season_year) as seasons,
               MIN(cs.season_year) as first_season,
               MAX(cs.season_year) as last_season,
               GROUP_CONCAT(DISTINCT t.abbreviation) as team_abbrevs
        FROM coaches c
        JOIN coach_seasons cs ON c.id = cs.coach_id
        JOIN teams t ON cs.team_id = t.id
        WHERE cs.season_type = 'Regular Season'
        GROUP BY c.id
        ORDER BY total_wins DESC
    """)
    return json_response(data)


@coach_app.route('/api/<coach_id:int>')
def api_coach_detail(coach_id):
    coach = query_db("""
        SELECT id as coach_id, name as coach_name
        FROM coaches WHERE id = ?
    """, (coach_id,), one=True)
    if not coach:
        response.status = 404
        return json_response({'error': 'Coach not found'})

    # Season-by-season  (template expects season, team_name, wins, losses, conf_rank)
    seasons = query_db("""
        SELECT cs.season_year as season, cs.wins, cs.losses, cs.season_type,
               t.full_name as team_name, t.abbreviation, t.id as team_id,
               ts.conf_rank, ts.playoff_result,
               ts.off_rating, ts.def_rating, ts.net_rating
        FROM coach_seasons cs
        JOIN teams t ON cs.team_id = t.id
        LEFT JOIN team_season_stats ts ON ts.team_id = cs.team_id
            AND ts.season_year = cs.season_year
        WHERE cs.coach_id = ?
        ORDER BY cs.season_year DESC
    """, (coach_id,))

    # Career totals
    career = query_db("""
        SELECT SUM(wins) as total_wins, SUM(losses) as total_losses,
               ROUND(CAST(SUM(wins) AS REAL) / NULLIF(SUM(wins)+SUM(losses), 0), 3) as win_pct,
               COUNT(DISTINCT team_id) as teams,
               COUNT(DISTINCT season_year) as total_seasons
        FROM coach_seasons WHERE coach_id = ? AND season_type = 'Regular Season'
    """, (coach_id,), one=True)

    coach['seasons'] = seasons
    coach['career'] = career
    return json_response(coach)


@coach_app.route('/api/rankings')
def api_coach_rankings():
    data = query_db("""
        SELECT c.id as coach_id, c.name as coach_name,
               SUM(cs.wins) as total_wins,
               SUM(cs.losses) as total_losses,
               ROUND(CAST(SUM(cs.wins) AS REAL) /
                   NULLIF(SUM(cs.wins) + SUM(cs.losses), 0), 3) as win_pct,
               COUNT(DISTINCT cs.season_year) as total_seasons,
               GROUP_CONCAT(DISTINCT t.abbreviation) as teams
        FROM coaches c
        JOIN coach_seasons cs ON c.id = cs.coach_id
        JOIN teams t ON cs.team_id = t.id
        WHERE cs.season_type = 'Regular Season'
        GROUP BY c.id
        HAVING total_seasons >= 3
        ORDER BY win_pct DESC
    """)
    return json_response(data)


@coach_app.route('/api/<coach_id:int>/impact')
def api_coach_impact(coach_id):
    # Template expects: season, team_name, wins, prev_wins, win_change
    data = query_db("""
        SELECT cs.season_year as season, t.full_name as team_name,
               t.abbreviation,
               cs.wins, cs.losses,
               LAG(cs.wins) OVER (PARTITION BY cs.team_id ORDER BY cs.season_year) as prev_wins
        FROM coach_seasons cs
        JOIN teams t ON cs.team_id = t.id
        WHERE cs.coach_id = ? AND cs.season_type = 'Regular Season'
        ORDER BY cs.season_year
    """, (coach_id,))

    # Add win_change
    result = []
    for row in data:
        r = dict(row)
        if r.get('prev_wins') is not None:
            r['win_change'] = r['wins'] - r['prev_wins']
        else:
            r['win_change'] = None
        result.append(r)

    # Return newest season first
    result.reverse()

    return json_response(result)
