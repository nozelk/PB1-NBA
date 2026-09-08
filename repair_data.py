"""
Data Repair & Retry Script
===========================
Fixes gaps from failed API calls during data collection.
Retries only what's missing — no full re-collection needed.

Sections:
  1. Retry failed player details (NULL position/country)
  2. Find & retry missing game seasons
  3. Search NBA API for missing high-salary players
  4. Re-import salaries after adding new players

Usage:
  python repair_data.py                # run all repairs
  python repair_data.py --players      # retry only player details
  python repair_data.py --games        # retry only missing games
  python repair_data.py --missing      # search & add missing players
  python repair_data.py --salaries     # re-import salaries
"""

import sys, os, time, json, sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, init_db

from nba_api.stats.static import players as nba_players_static
from nba_api.stats.endpoints import (
    commonplayerinfo,
    teamgamelog,
    playercareerstats,
    commonteamroster,
)

SEASON_START = 2004
_now = datetime.now()
SEASON_END = _now.year if _now.month >= 10 else _now.year - 1
DELAY = 2.0  # slightly higher delay for retries (be nice to API)
MAX_RETRIES = 3


def season_str(year):
    return f"{year}-{str(year+1)[-2:]}"


def safe_int(val, default=None):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def safe_float(val, default=None):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _api_call_with_retry(func, retries=MAX_RETRIES, delay=DELAY):
    """Call an API function with retry logic."""
    for attempt in range(retries):
        try:
            result = func()
            time.sleep(delay)
            return result
        except Exception as e:
            if attempt < retries - 1:
                wait = delay * (attempt + 2)
                print(f"      ↻ retry {attempt+2}/{retries} in {wait:.0f}s... ({e})")
                time.sleep(wait)
            else:
                raise e


# ============================================================
# 1. RETRY FAILED PLAYER DETAILS
# ============================================================
def retry_player_details():
    """Re-fetch details for players missing position/country/etc."""
    print("\n" + "=" * 60)
    print("  REPAIR: Player Details (NULL position/country)")
    print("=" * 60)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, display_name FROM players
        WHERE position IS NULL OR position = ''
           OR country IS NULL OR country = ''
    """)
    players = cursor.fetchall()
    total = len(players)

    if total == 0:
        print("  ✓ All players have details — nothing to fix!")
        conn.close()
        return

    print(f"  Found {total} players missing details\n")
    fixed = 0
    failed = []

    for i, player in enumerate(players):
        pid = player['id']
        name = player['display_name']
        try:
            def call():
                return commonplayerinfo.CommonPlayerInfo(player_id=pid)
            info = _api_call_with_retry(call)
            df = info.common_player_info.get_data_frame()

            if len(df) > 0:
                row = df.iloc[0]
                cursor.execute('''
                    UPDATE players SET
                        position = ?, height = ?, weight = ?, country = ?,
                        school = ?, birthdate = ?, draft_year = ?,
                        draft_round = ?, draft_number = ?,
                        from_year = ?, to_year = ?
                    WHERE id = ?
                ''', (row.get('POSITION'), row.get('HEIGHT'), safe_int(row.get('WEIGHT')),
                      row.get('COUNTRY'), row.get('SCHOOL'), row.get('BIRTHDATE'),
                      safe_int(row.get('DRAFT_YEAR')), safe_int(row.get('DRAFT_ROUND')),
                      safe_int(row.get('DRAFT_NUMBER')),
                      safe_int(row.get('FROM_YEAR')), safe_int(row.get('TO_YEAR')),
                      pid))
                fixed += 1

            if (i + 1) % 25 == 0:
                conn.commit()
                print(f"    {i+1}/{total} processed ({fixed} fixed)...")

        except Exception as e:
            failed.append((name, str(e)))
            print(f"    ✗ {name}: {e}")

    conn.commit()
    conn.close()
    print(f"\n  ✓ Fixed {fixed}/{total} players")
    if failed:
        print(f"  ✗ Still failed: {len(failed)}")
        for name, err in failed[:10]:
            print(f"      - {name}: {err[:60]}")


# ============================================================
# 2. FIND & RETRY MISSING GAME SEASONS
# ============================================================
def retry_missing_games():
    """Find team/season combos with 0 games and retry them."""
    print("\n" + "=" * 60)
    print("  REPAIR: Missing Game Seasons")
    print("=" * 60)

    conn = get_db()
    cursor = conn.cursor()

    # Build abbreviation -> team_id lookup
    cursor.execute("SELECT id, abbreviation, full_name FROM teams")
    teams = cursor.fetchall()
    abbrev_to_id = {t['abbreviation']: t['id'] for t in teams}

    # Find gaps: which team/season combos have no games?
    missing = []
    for team in teams:
        tid = team['id']
        for year in range(SEASON_START, SEASON_END + 1):
            cnt = cursor.execute(
                "SELECT COUNT(*) as c FROM games WHERE team_id=? AND season_year=?",
                (tid, year)).fetchone()['c']
            if cnt == 0:
                missing.append((tid, team['full_name'], year))

    if not missing:
        print("  ✓ No missing game seasons — all complete!")
        conn.close()
        return

    print(f"  Found {len(missing)} missing team/season combos\n")
    fixed = 0
    failed = []

    for tid, team_name, year in missing:
        try:
            def call():
                return teamgamelog.TeamGameLog(team_id=tid, season=season_str(year))
            log = _api_call_with_retry(call)
            df = log.get_data_frames()[0]

            count = 0
            for _, row in df.iterrows():
                game_id = row['Game_ID']
                matchup = row.get('MATCHUP', '')

                opponent_id = None
                if matchup:
                    parts = matchup.replace(' vs. ', ' @ ').split(' @ ')
                    if len(parts) == 2:
                        opp_abbrev = parts[1].strip()
                        opponent_id = abbrev_to_id.get(opp_abbrev)

                pts = safe_int(row.get('PTS'))
                plus_minus = safe_float(row.get('PLUS_MINUS'))
                opp_pts = pts - int(plus_minus) if pts and plus_minus is not None else None

                cursor.execute('''
                    INSERT OR IGNORE INTO games
                    (game_id, season_year, game_date, matchup, team_id, opponent_id,
                     wl, pts, opp_pts, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct,
                     ftm, fta, ft_pct, oreb, dreb, reb, ast, stl, blk, tov, pf,
                     plus_minus, season_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (game_id, year, row.get('GAME_DATE'), matchup, tid, opponent_id,
                      row.get('WL'), pts, opp_pts,
                      safe_float(row.get('FGM')), safe_float(row.get('FGA')), safe_float(row.get('FG_PCT')),
                      safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                      safe_float(row.get('FTM')), safe_float(row.get('FTA')), safe_float(row.get('FT_PCT')),
                      safe_float(row.get('OREB')), safe_float(row.get('DREB')), safe_float(row.get('REB')),
                      safe_float(row.get('AST')), safe_float(row.get('STL')), safe_float(row.get('BLK')),
                      safe_float(row.get('TOV')), safe_float(row.get('PF')),
                      plus_minus, 'Regular Season'))
                count += 1

            conn.commit()
            print(f"    ✓ {team_name} {year}: {count} games")
            fixed += 1

        except Exception as e:
            failed.append((team_name, year, str(e)))
            print(f"    ✗ {team_name} {year}: {e}")

    conn.close()
    print(f"\n  ✓ Fixed {fixed}/{len(missing)} missing seasons")
    if failed:
        print(f"  ✗ Still failed: {len(failed)}")
        for name, yr, err in failed:
            print(f"      - {name} {yr}: {err[:60]}")


# ============================================================
# 3. SEARCH & ADD MISSING HIGH-SALARY PLAYERS
# ============================================================
def add_missing_players():
    """Try to find unmatched salary players in the NBA API and add them."""
    print("\n" + "=" * 60)
    print("  REPAIR: Add Missing High-Salary Players")
    print("=" * 60)

    unmatched_path = os.path.join(os.path.dirname(__file__), 'files', 'salaries_unmatched.json')
    if not os.path.exists(unmatched_path):
        print("  ✗ No salaries_unmatched.json found")
        return

    with open(unmatched_path, 'r', encoding='utf-8') as f:
        unmatched = json.load(f)

    # Group by name, find those with high salaries
    from collections import defaultdict
    by_name = defaultdict(list)
    for u in unmatched:
        by_name[u['player_name']].append(u)

    # Only try players with salary > $500K (meaningful NBA players)
    high_value = {name: entries for name, entries in by_name.items()
                  if sum(e['salary'] for e in entries) > 500_000}

    if not high_value:
        print("  ✓ No high-salary unmatched players to search for")
        return

    print(f"  Searching NBA API for {len(high_value)} high-salary players...\n")

    # Search NBA static player list (includes historical players)
    all_nba_players = nba_players_static.get_players()
    nba_by_lastname = defaultdict(list)
    for p in all_nba_players:
        nba_by_lastname[p['last_name'].lower()].append(p)

    conn = get_db()
    cursor = conn.cursor()
    added = 0
    found_details = 0

    for hh_name, entries in sorted(high_value.items(), key=lambda x: -sum(e['salary'] for e in x[1])):
        total_sal = sum(e['salary'] for e in entries)
        parts = hh_name.split()
        if len(parts) < 2:
            continue
        first = parts[0]
        last = parts[-1]

        # Search in NBA static list
        candidates = nba_by_lastname.get(last.lower(), [])
        # Filter by first name similarity
        matches = [p for p in candidates if p['first_name'].lower().startswith(first[0].lower())]

        if len(matches) == 1:
            nba_p = matches[0]
            pid = nba_p['id']

            # Check if already in DB
            existing = cursor.execute("SELECT id FROM players WHERE id=?", (pid,)).fetchone()
            if existing:
                print(f"    ≈ {hh_name} → already in DB as id={pid} (name mismatch?)")
                continue

            # Add player to DB
            cursor.execute('''
                INSERT OR IGNORE INTO players (id, first_name, last_name, display_name)
                VALUES (?, ?, ?, ?)
            ''', (pid, nba_p['first_name'], nba_p['last_name'], nba_p['full_name']))
            added += 1
            print(f"    + {hh_name} → added as {nba_p['full_name']} (id={pid}, ${total_sal:,})")

            # Try to get details
            try:
                def call():
                    return commonplayerinfo.CommonPlayerInfo(player_id=pid)
                info = _api_call_with_retry(call)
                df = info.common_player_info.get_data_frame()
                if len(df) > 0:
                    row = df.iloc[0]
                    cursor.execute('''
                        UPDATE players SET
                            position = ?, height = ?, weight = ?, country = ?,
                            school = ?, birthdate = ?, draft_year = ?,
                            draft_round = ?, draft_number = ?,
                            from_year = ?, to_year = ?
                        WHERE id = ?
                    ''', (row.get('POSITION'), row.get('HEIGHT'), safe_int(row.get('WEIGHT')),
                          row.get('COUNTRY'), row.get('SCHOOL'), row.get('BIRTHDATE'),
                          safe_int(row.get('DRAFT_YEAR')), safe_int(row.get('DRAFT_ROUND')),
                          safe_int(row.get('DRAFT_NUMBER')),
                          safe_int(row.get('FROM_YEAR')), safe_int(row.get('TO_YEAR')), pid))
                    found_details += 1
            except Exception as e:
                print(f"      (details failed: {e})")

            # Try to get career stats
            try:
                def call2():
                    return playercareerstats.PlayerCareerStats(player_id=pid)
                career = _api_call_with_retry(call2)
                df = career.season_totals_regular_season.get_data_frame()
                for _, row in df.iterrows():
                    year_str = row.get('SEASON_ID', '')
                    if '-' not in year_str:
                        continue
                    year = int(year_str.split('-')[0])
                    if year < SEASON_START or year > SEASON_END:
                        continue
                    team_id = safe_int(row.get('TEAM_ID'))
                    cursor.execute('''
                        INSERT OR REPLACE INTO player_season_stats
                        (player_id, team_id, season_year, age, gp, gs, min,
                         fgm, fga, fg_pct, fg3m, fg3a, fg3_pct,
                         ftm, fta, ft_pct, oreb, dreb, reb,
                         ast, stl, blk, tov, pf, pts, plus_minus)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (pid, team_id, year,
                          safe_int(row.get('PLAYER_AGE')),
                          safe_int(row.get('GP')), safe_int(row.get('GS')),
                          safe_float(row.get('MIN')),
                          safe_float(row.get('FGM')), safe_float(row.get('FGA')), safe_float(row.get('FG_PCT')),
                          safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                          safe_float(row.get('FTM')), safe_float(row.get('FTA')), safe_float(row.get('FT_PCT')),
                          safe_float(row.get('OREB')), safe_float(row.get('DREB')), safe_float(row.get('REB')),
                          safe_float(row.get('AST')), safe_float(row.get('STL')), safe_float(row.get('BLK')),
                          safe_float(row.get('TOV')), safe_float(row.get('PF')), safe_float(row.get('PTS')),
                          safe_float(row.get('PLUS_MINUS'))))
            except Exception as e:
                print(f"      (career stats failed: {e})")

        elif len(matches) > 1:
            names = [m['full_name'] for m in matches]
            print(f"    ? {hh_name} → multiple matches: {names} (skipped)")
        else:
            print(f"    - {hh_name} → not found in NBA API (${total_sal:,})")

    conn.commit()
    conn.close()
    print(f"\n  ✓ Added {added} new players ({found_details} with details)")

    if added > 0:
        print("  → Run 'python repair_data.py --salaries' to re-import salaries for new players")


# ============================================================
# 4. RE-IMPORT SALARIES (after adding new players)
# ============================================================
def reimport_salaries():
    """Clear and re-import salaries with current player DB."""
    print("\n" + "=" * 60)
    print("  REPAIR: Re-import Salaries")
    print("=" * 60)

    conn = get_db()
    conn.execute("DELETE FROM salaries")
    conn.commit()
    conn.close()
    print("  Cleared salaries table")

    from collect_salaries import import_salaries_to_db
    import_salaries_to_db()


# ============================================================
# 5. QUICK DATA SUMMARY
# ============================================================
def show_summary():
    """Show current DB stats and any remaining gaps."""
    print("\n" + "=" * 60)
    print("  DATABASE SUMMARY")
    print("=" * 60)

    conn = get_db()
    cursor = conn.cursor()

    tables = ['teams', 'players', 'team_season_stats', 'player_season_stats',
              'games', 'rosters', 'coaches', 'coach_seasons', 'salaries', 'awards']
    for table in tables:
        try:
            cnt = cursor.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()['c']
            print(f"    {table:25s} {cnt:>8,} rows")
        except:
            print(f"    {table:25s}        0 rows")

    # Players missing details
    missing_details = cursor.execute(
        "SELECT COUNT(*) as c FROM players WHERE position IS NULL OR position = ''").fetchone()['c']
    total_players = cursor.execute("SELECT COUNT(*) as c FROM players").fetchone()['c']
    print(f"\n    Players missing details: {missing_details}/{total_players}")

    # Games per season check
    print(f"\n    Games coverage by season:")
    for year in range(SEASON_START, SEASON_END + 1):
        cnt = cursor.execute(
            "SELECT COUNT(DISTINCT game_id) as c FROM games WHERE season_year=?",
            (year,)).fetchone()['c']
        teams_with_games = cursor.execute(
            "SELECT COUNT(DISTINCT team_id) as c FROM games WHERE season_year=?",
            (year,)).fetchone()['c']
        status = "✓" if teams_with_games >= 30 else f"⚠ only {teams_with_games} teams"
        print(f"      {year}-{year+1}: {cnt:>5} games, {teams_with_games} teams  {status}")

    # Salary coverage
    sal_players = cursor.execute(
        "SELECT COUNT(DISTINCT player_id) as c FROM salaries").fetchone()['c']
    print(f"\n    Salary coverage: {sal_players} players with salary data")

    conn.close()


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    init_db()

    args = sys.argv[1:]

    if not args or '--all' in args:
        # Run all repairs
        show_summary()
        retry_player_details()
        retry_missing_games()
        add_missing_players()
        reimport_salaries()
        print("\n")
        show_summary()
    else:
        if '--summary' in args:
            show_summary()
        if '--players' in args:
            retry_player_details()
        if '--games' in args:
            retry_missing_games()
        if '--missing' in args:
            add_missing_players()
        if '--salaries' in args:
            reimport_salaries()

    print("\n  Done!")
