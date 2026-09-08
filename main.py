from bottle import Bottle, run, static_file, template, TEMPLATE_PATH, response, request
import json





from database import query_db, init_db


TEMPLATE_PATH.append('./templates')

app = Bottle()







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
    return template('home', totals={
        'teams': query_db('SELECT COUNT(*) AS c FROM teams', one=True)['c'],
        'seasons': query_db('SELECT COUNT(DISTINCT season_year) AS c FROM team_season_stats', one=True)['c'],
        'players': query_db('SELECT COUNT(*) AS c FROM players', one=True)['c'],
        'games': query_db('SELECT COUNT(DISTINCT game_id) AS c FROM games', one=True)['c'],
        'coaches': query_db('SELECT COUNT(*) AS c FROM coaches', one=True)['c'],
    })








# ============================================================
# DASHBOARD API
# ============================================================


# ============================================================
# LEADERS API
# ============================================================


# ============================================================
# COMPARE API
# ============================================================




# ============================================================
# SALARY API
# ============================================================




# ============================================================
# SEARCH API
# ============================================================


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


# ============================================================
# PLAYER OF THE WEEK / MONTH API
# ============================================================


# ============================================================
# TOP RATED PLAYERS API  (Hollinger PER – same as Basketball Reference)
# ============================================================


# ============================================================
# RECENT / FEATURED GAMES API
# ============================================================


if __name__ == '__main__':
    init_db()
    print(f"Template paths: {TEMPLATE_PATH}")
    run(app, host='localhost', port=8080, debug=True, reloader=True)