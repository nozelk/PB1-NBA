"""
Admin module – secret URL /nba/admin
- Login page (hardcoded admin credentials)
- Dashboard showing DB status (row counts, missing data)
- Refresh buttons per data category that trigger collection
- Staging mode: collect → preview → confirm/cancel
"""
from bottle import Bottle, request, response, template, redirect
from database import query_db, get_db, set_db_override, clear_db_override, DB_PATH, STAGING_PATH, BACKUP_DIR
import json
import hashlib
import threading
import shutil
import os
import sqlite3
from datetime import datetime

admin_app = Bottle()

# ── Credentials (change these!) ──────────────────────────────
ADMIN_USER = "admin"
ADMIN_PASS_HASH = hashlib.sha256("nba2025admin".encode()).hexdigest()
SECRET_TOKEN = "nba_admin_session_token_x7k9"   # simple cookie token


def json_response(data):
    response.content_type = 'application/json'
    return json.dumps(data, default=str)


def _is_logged_in():
    return request.get_cookie("admin_token") == SECRET_TOKEN


def _require_login():
    if not _is_logged_in():
        redirect('/nba/admin/login')


# ============================================================
# PAGES
# ============================================================
@admin_app.route('/login')
def login_page():
    return template('admin_login')


@admin_app.route('/login', method='POST')
def login_submit():
    user = request.forms.get('username', '')
    pwd = request.forms.get('password', '')
    pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()

    if user == ADMIN_USER and pwd_hash == ADMIN_PASS_HASH:
        response.set_cookie("admin_token", SECRET_TOKEN, path="/")
        redirect('/nba/admin')
    else:
        return template('admin_login', error="Wrong username or password.")


@admin_app.route('/logout')
def logout():
    response.delete_cookie("admin_token", path="/")
    redirect('/nba/admin/login')


@admin_app.route('/')
def admin_dashboard():
    _require_login()
    return template('admin_dashboard')


# ============================================================
# API: Database status
# ============================================================
@admin_app.route('/api/status')
def api_status():
    _require_login()
    from collect_all import SEASON_START, SEASON_END

    tables = ['teams', 'players', 'team_season_stats', 'player_season_stats',
              'games', 'player_game_stats', 'rosters', 'coaches', 'coach_seasons',
              'salaries', 'awards']

    counts = {}
    for t in tables:
        try:
            row = query_db(f"SELECT COUNT(*) as c FROM {t}", one=True)
            counts[t] = row['c'] if row else 0
        except Exception:
            counts[t] = 0

    # Season coverage
    season_coverage = {}
    try:
        rows = query_db("SELECT season_year, COUNT(*) as c FROM team_season_stats GROUP BY season_year ORDER BY season_year")
        season_coverage['team_season_stats'] = {r['season_year']: r['c'] for r in rows}
    except Exception:
        season_coverage['team_season_stats'] = {}

    try:
        rows = query_db("SELECT season_year, COUNT(*) as c FROM player_season_stats GROUP BY season_year ORDER BY season_year")
        season_coverage['player_season_stats'] = {r['season_year']: r['c'] for r in rows}
    except Exception:
        season_coverage['player_season_stats'] = {}

    try:
        rows = query_db("SELECT season_year, COUNT(*) as c FROM games GROUP BY season_year ORDER BY season_year")
        season_coverage['games'] = {r['season_year']: r['c'] for r in rows}
    except Exception:
        season_coverage['games'] = {}

    # Players missing details
    try:
        missing_details = query_db(
            "SELECT COUNT(*) as c FROM players WHERE position IS NULL OR country IS NULL", one=True)
        missing_details_count = missing_details['c'] if missing_details else 0
    except Exception:
        missing_details_count = 0

    return json_response({
        'counts': counts,
        'season_range': {'start': SEASON_START, 'end': SEASON_END},
        'season_coverage': season_coverage,
        'missing_player_details': missing_details_count,
    })


# ============================================================
# API: Refresh data (staging → preview → confirm/cancel)
# ============================================================
_running_tasks = {}   # task_name -> {"status": "running"|"done"|"error"|"staged", "message": "..."}
_staging_info = {}    # task_name -> {"before": {...}, "after": {...}, "tables": [...]}

# Which tables each task affects
_TASK_TABLES = {
    'teams': ['teams'],
    'team_season_stats': ['team_season_stats'],
    'players': ['players', 'player_season_stats'],
    'player_details': ['players'],
    'games': ['games'],
    'player_game_stats': ['player_game_stats'],
    'rosters': ['rosters'],
    'coaches': ['coaches', 'coach_seasons'],
    'salaries': ['salaries'],
    'awards': ['awards'],
}


def _get_table_counts(db_path, tables):
    """Get row counts for specified tables from a given DB file."""
    counts = {}
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        for t in tables:
            try:
                row = conn.execute(f"SELECT COUNT(*) as c FROM {t}").fetchone()
                counts[t] = row[0] if row else 0
            except Exception:
                counts[t] = 0
        conn.close()
    except Exception:
        for t in tables:
            counts[t] = 0
    return counts


def _get_all_table_counts(db_path):
    """Get row counts for ALL tables from a given DB file."""
    all_tables = ['teams', 'players', 'team_season_stats', 'player_season_stats',
                  'games', 'player_game_stats', 'rosters', 'coaches', 'coach_seasons',
                  'salaries', 'awards']
    return _get_table_counts(db_path, all_tables)


def _create_backup():
    """Create a timestamped backup of the main database. Returns backup path."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'nba_backup_{timestamp}.db')
    shutil.copy2(DB_PATH, backup_path)
    return backup_path


def _run_staging_collection(task_name, func, tables):
    """Run collection into staging DB, then report diff."""
    _running_tasks[task_name] = {"status": "running", "message": "Collecting data (staging)..."}
    try:
        # Get "before" counts from main DB
        before = _get_table_counts(DB_PATH, tables)

        # Copy main DB to staging
        if os.path.exists(STAGING_PATH):
            os.remove(STAGING_PATH)
        shutil.copy2(DB_PATH, STAGING_PATH)

        # Run collection with DB override pointing to staging
        set_db_override(STAGING_PATH)
        try:
            func()
        finally:
            clear_db_override()

        # Get "after" counts from staging
        after = _get_table_counts(STAGING_PATH, tables)

        # Build diff summary
        changes = []
        for t in tables:
            diff = after.get(t, 0) - before.get(t, 0)
            sign = f"+{diff}" if diff > 0 else str(diff)
            changes.append(f"{t}: {before.get(t,0)} → {after.get(t,0)} ({sign})")

        _staging_info[task_name] = {
            'before': before,
            'after': after,
            'tables': tables,
        }
        _running_tasks[task_name] = {
            "status": "staged",
            "message": "Ready for review. " + " | ".join(changes),
            "preview": {
                'before': before,
                'after': after,
                'changes': changes,
            }
        }
    except Exception as e:
        clear_db_override()
        # Clean up staging on error
        if os.path.exists(STAGING_PATH):
            os.remove(STAGING_PATH)
        _running_tasks[task_name] = {"status": "error", "message": str(e)}


@admin_app.route('/api/refresh', method='POST')
def api_refresh():
    _require_login()
    body = request.json or {}
    task = body.get('task', '')

    from collect_all import (
        collect_teams, collect_team_season_stats, collect_games,
        collect_players_and_stats, collect_player_details,
        collect_player_game_stats, collect_rosters,
        collect_coaches, collect_salaries, collect_awards,
    )

    task_map = {
        'teams': collect_teams,
        'team_season_stats': collect_team_season_stats,
        'players': collect_players_and_stats,
        'player_details': collect_player_details,
        'games': collect_games,
        'player_game_stats': collect_player_game_stats,
        'rosters': collect_rosters,
        'coaches': collect_coaches,
        'salaries': collect_salaries,
        'awards': collect_awards,
    }

    if task not in task_map:
        response.status = 400
        return json_response({'error': f'Unknown task: {task}', 'available': list(task_map.keys())})

    if task in _running_tasks and _running_tasks[task].get('status') == 'running':
        return json_response({'status': 'already_running', 'message': f'{task} is already running.'})

    tables = _TASK_TABLES.get(task, [])
    t = threading.Thread(
        target=_run_staging_collection,
        args=(task, task_map[task], tables),
        daemon=True
    )
    t.start()

    return json_response({'status': 'started', 'task': task})


@admin_app.route('/api/refresh/confirm', method='POST')
def api_refresh_confirm():
    """Confirm staged data: backup main DB, replace with staging."""
    _require_login()
    body = request.json or {}
    task = body.get('task', '')

    if task not in _running_tasks:
        response.status = 400
        return json_response({'error': f'No task: {task}'})

    if _running_tasks[task].get('status') != 'staged':
        response.status = 400
        return json_response({'error': f'Task {task} is not in staged state (status: {_running_tasks[task].get("status")})'})

    if not os.path.exists(STAGING_PATH):
        response.status = 400
        return json_response({'error': 'Staging database not found.'})

    try:
        # Create backup of current DB
        backup_path = _create_backup()

        # Replace main DB with staging
        shutil.copy2(STAGING_PATH, DB_PATH)
        os.remove(STAGING_PATH)

        info = _staging_info.pop(task, {})
        after = info.get('after', {})
        _running_tasks[task] = {
            "status": "done",
            "message": f"Confirmed & applied. Backup: {os.path.basename(backup_path)}"
        }
        return json_response({
            'status': 'confirmed',
            'backup': os.path.basename(backup_path),
            'counts': after,
        })
    except Exception as e:
        _running_tasks[task] = {"status": "error", "message": f"Confirm failed: {e}"}
        response.status = 500
        return json_response({'error': str(e)})


@admin_app.route('/api/refresh/cancel', method='POST')
def api_refresh_cancel():
    """Cancel staged data: delete staging DB."""
    _require_login()
    body = request.json or {}
    task = body.get('task', '')

    if os.path.exists(STAGING_PATH):
        os.remove(STAGING_PATH)

    _staging_info.pop(task, None)
    if task in _running_tasks:
        _running_tasks[task] = {"status": "cancelled", "message": "Cancelled by user."}

    return json_response({'status': 'cancelled', 'task': task})


@admin_app.route('/api/refresh/all', method='POST')
def api_refresh_all():
    """Run ALL collection steps sequentially in background with backup."""
    _require_login()

    from collect_all import (
        collect_teams, collect_team_season_stats, collect_games,
        collect_players_and_stats, collect_player_details,
        collect_rosters, collect_coaches, collect_salaries,
    )

    steps = [
        ('teams', collect_teams),
        ('team_season_stats', collect_team_season_stats),
        ('players', collect_players_and_stats),
        ('player_details', collect_player_details),
        ('games', collect_games),
        ('rosters', collect_rosters),
        ('coaches', collect_coaches),
        ('salaries', collect_salaries),
    ]

    def run_all():
        _running_tasks['all'] = {"status": "running", "message": "Creating backup..."}
        try:
            backup_path = _create_backup()
            _running_tasks['all']['message'] = f"Backup created: {os.path.basename(backup_path)}. Starting collection..."
        except Exception as e:
            _running_tasks['all'] = {"status": "error", "message": f"Backup failed: {e}"}
            return

        for name, func in steps:
            _running_tasks['all']['message'] = f"Running: {name}..."
            _running_tasks[name] = {"status": "running", "message": "Running..."}
            try:
                func()
                _running_tasks[name] = {"status": "done", "message": "OK"}
            except Exception as e:
                _running_tasks[name] = {"status": "error", "message": str(e)}
        _running_tasks['all'] = {"status": "done", "message": f"All steps completed. Backup: {os.path.basename(backup_path)}"}

    if 'all' in _running_tasks and _running_tasks['all'].get('status') == 'running':
        return json_response({'status': 'already_running'})

    t = threading.Thread(target=run_all, daemon=True)
    t.start()
    return json_response({'status': 'started', 'task': 'all'})


@admin_app.route('/api/backups')
def api_list_backups():
    """List available database backups."""
    _require_login()
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backups = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.endswith('.db'):
            path = os.path.join(BACKUP_DIR, f)
            size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)
            backups.append({'filename': f, 'size_mb': size_mb})
    return json_response(backups)


@admin_app.route('/api/backups/restore', method='POST')
def api_restore_backup():
    """Restore a specific backup."""
    _require_login()
    body = request.json or {}
    filename = body.get('filename', '')

    if not filename or '..' in filename:
        response.status = 400
        return json_response({'error': 'Invalid filename'})

    backup_path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(backup_path):
        response.status = 404
        return json_response({'error': 'Backup not found'})

    try:
        # Backup current before restoring (safety net)
        safety_backup = _create_backup()
        shutil.copy2(backup_path, DB_PATH)
        return json_response({
            'status': 'restored',
            'restored_from': filename,
            'safety_backup': os.path.basename(safety_backup),
        })
    except Exception as e:
        response.status = 500
        return json_response({'error': str(e)})


@admin_app.route('/api/refresh/status')
def api_refresh_status():
    _require_login()
    return json_response(_running_tasks)


# ============================================================
# API: Player Game Stats — per-season collection with retry
# ============================================================
@admin_app.route('/api/player-stats/coverage')
def api_player_stats_coverage():
    """Full coverage view: expected players vs collected, per season."""
    _require_login()
    from collect_all import SEASON_START, SEASON_END

    # Expected players per season (from player_season_stats)
    expected_rows = query_db("""
        SELECT season_year, COUNT(DISTINCT player_id) as expected
        FROM player_season_stats WHERE gp >= 1
        GROUP BY season_year ORDER BY season_year
    """)
    expected_map = {r['season_year']: r['expected'] for r in expected_rows}

    # Collected game stats per season
    collected_rows = query_db("""
        SELECT season_year, COUNT(*) as total_rows,
               COUNT(DISTINCT player_id) as collected
        FROM player_game_stats
        GROUP BY season_year ORDER BY season_year
    """)
    collected_map = {r['season_year']: {'rows': r['total_rows'], 'collected': r['collected']} for r in collected_rows}

    seasons = []
    for year in range(SEASON_START, SEASON_END + 1):
        exp = expected_map.get(year, 0)
        col_info = collected_map.get(year, {'rows': 0, 'collected': 0})
        col = col_info['collected']
        rows = col_info['rows']
        missing = max(0, exp - col)
        status = 'complete' if col >= exp and exp > 0 else 'partial' if col > 0 else 'empty'
        seasons.append({
            'season': year,
            'expected_players': exp,
            'collected_players': col,
            'missing_players': missing,
            'total_rows': rows,
            'status': status,
        })

    # Check active tasks
    active = {}
    for key, val in _running_tasks.items():
        if key.startswith('game_stats_') and val.get('status') == 'running':
            try:
                yr = int(key.split('_')[-1])
                active[yr] = val.get('message', 'Running...')
            except ValueError:
                pass

    return json_response({'seasons': seasons, 'active_tasks': active})


@admin_app.route('/api/player-stats/collect', method='POST')
def api_player_stats_collect():
    """Collect player game stats for a specific season. Pass retry=true to only collect missing players."""
    _require_login()
    body = request.json or {}
    season = int(body.get('season', 2025))
    retry_missing = body.get('retry', False)
    task_name = f'game_stats_{season}'

    if task_name in _running_tasks and _running_tasks[task_name].get('status') == 'running':
        return json_response({'status': 'already_running', 'message': f'Already running for {season}.'})

    from collect_game_stats import collect as collect_game_stats_season

    def run():
        season_label = f"{season}-{str(season+1)[-2:]}"
        conn = get_db()
        cursor = conn.cursor()

        if retry_missing:
            # Find players who have season stats but no game stats
            cursor.execute("""
                SELECT DISTINCT ps.player_id, ps.team_id
                FROM player_season_stats ps
                WHERE ps.season_year = ? AND ps.gp >= 1
                  AND ps.player_id NOT IN (
                      SELECT DISTINCT player_id FROM player_game_stats WHERE season_year = ?
                  )
                ORDER BY ps.pts DESC
            """, (season, season))
            missing_players = [(row['player_id'], row['team_id']) for row in cursor.fetchall()]
            conn.close()

            if not missing_players:
                _running_tasks[task_name] = {"status": "done", "message": f"No missing players for {season_label}!"}
                return

            _running_tasks[task_name] = {"status": "running", "message": f"Retrying {len(missing_players)} missing players for {season_label}..."}

            # Import needed modules
            from nba_api.stats.endpoints import playergamelog
            import time

            def safe_float(val, default=None):
                try: return float(val)
                except (TypeError, ValueError): return default

            conn2 = get_db()
            cur2 = conn2.cursor()

            # Build abbreviation -> team_id
            cur2.execute("SELECT id, abbreviation FROM teams")
            abbr_to_id = {row['abbreviation']: row['id'] for row in cur2.fetchall()}

            total_inserted = 0
            for idx, (player_id, default_team_id) in enumerate(missing_players):
                try:
                    log = playergamelog.PlayerGameLog(player_id=player_id, season=season_label)
                    df = log.get_data_frames()[0]

                    if len(df) == 0:
                        time.sleep(1.5)
                        continue

                    for _, row in df.iterrows():
                        pts = safe_float(row.get('PTS'), 0)
                        fgm = safe_float(row.get('FGM'), 0)
                        fga = safe_float(row.get('FGA'), 0)
                        fta = safe_float(row.get('FTA'), 0)
                        ftm = safe_float(row.get('FTM'), 0)
                        oreb = safe_float(row.get('OREB'), 0)
                        dreb = safe_float(row.get('DREB'), 0)
                        stl = safe_float(row.get('STL'), 0)
                        ast = safe_float(row.get('AST'), 0)
                        blk = safe_float(row.get('BLK'), 0)
                        pf = safe_float(row.get('PF'), 0)
                        tov = safe_float(row.get('TOV'), 0)

                        game_score = round(
                            pts + 0.4*fgm - 0.7*fga - 0.4*(fta-ftm)
                            + 0.7*oreb + 0.3*dreb + stl + 0.7*ast
                            + 0.7*blk - 0.4*pf - tov, 1
                        )

                        matchup = row.get('MATCHUP', '')
                        team_abbr = matchup.split(' ')[0] if matchup else ''
                        team_id = abbr_to_id.get(team_abbr, default_team_id)

                        cur2.execute('''
                            INSERT OR IGNORE INTO player_game_stats
                            (player_id, team_id, game_id, season_year, game_date, matchup, wl,
                             min, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct,
                             ftm, fta, ft_pct, oreb, dreb, reb,
                             ast, stl, blk, tov, pf, pts, plus_minus, game_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (player_id, team_id, row.get('Game_ID'), season,
                              row.get('GAME_DATE'), matchup, row.get('WL'),
                              safe_float(row.get('MIN')),
                              fgm, fga, safe_float(row.get('FG_PCT')),
                              safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                              ftm, fta, safe_float(row.get('FT_PCT')),
                              oreb, dreb, safe_float(row.get('REB')),
                              ast, stl, blk, tov, pf, pts,
                              safe_float(row.get('PLUS_MINUS')), game_score))
                        total_inserted += 1

                    time.sleep(1.5)
                except Exception as e:
                    if 'rate' in str(e).lower() or '429' in str(e):
                        _running_tasks[task_name]['message'] = f"Rate limited, waiting 30s... ({idx+1}/{len(missing_players)})"
                        time.sleep(30)

                if (idx + 1) % 10 == 0:
                    conn2.commit()
                    _running_tasks[task_name]['message'] = f"Retry: {idx+1}/{len(missing_players)} players... ({total_inserted} rows added)"

            conn2.commit()
            conn2.close()

            # Final count
            final = query_db("SELECT COUNT(DISTINCT player_id) as c FROM player_game_stats WHERE season_year = ?", (season,), one=True)
            final_count = final['c'] if final else 0
            _running_tasks[task_name] = {
                "status": "done",
                "message": f"Retry done! Added {total_inserted} rows. Now {final_count} players for {season_label}."
            }
        else:
            # Full collection for this season
            _running_tasks[task_name] = {"status": "running", "message": f"Collecting game stats for {season_label} (all players)..."}
            conn.close()
            try:
                collect_game_stats_season(season)
                row = query_db("SELECT COUNT(*) as c, COUNT(DISTINCT player_id) as p FROM player_game_stats WHERE season_year = ?", (season,), one=True)
                count = row['c'] if row else 0
                players = row['p'] if row else 0
                _running_tasks[task_name] = {"status": "done", "message": f"Done! {count} rows, {players} players for {season_label}."}
            except Exception as e:
                _running_tasks[task_name] = {"status": "error", "message": str(e)}

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return json_response({'status': 'started', 'task': task_name, 'season': season, 'retry': retry_missing})


@admin_app.route('/api/game-stats-coverage')
def api_game_stats_coverage():
    """Show which seasons have game stats collected."""
    _require_login()
    rows = query_db("""
        SELECT season_year, COUNT(*) as total_rows,
               COUNT(DISTINCT player_id) as players
        FROM player_game_stats
        GROUP BY season_year ORDER BY season_year DESC
    """)
    return json_response([dict(r) for r in rows] if rows else [])


@admin_app.route('/api/salary-check')
def api_salary_check():
    """Run salary health check and return JSON report."""
    _require_login()
    from check_salaries import run_check
    report = run_check(as_json=True)
    return json_response(report)
