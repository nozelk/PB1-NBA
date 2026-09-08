"""
Collector: player game stats per season.
Usage: python collect_game_stats.py [season_year]
  e.g. python collect_game_stats.py 2025
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, query_db
from nba_api.stats.endpoints import playergamelog

DELAY = 1.2


def safe_float(val, default=None):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def collect(season=2025):
    season_str = f"{season}-{str(season+1)[-2:]}"
    conn = get_db()
    cursor = conn.cursor()

    # Build abbreviation -> team_id lookup
    cursor.execute("SELECT id, abbreviation FROM teams")
    abbr_to_id = {row['abbreviation']: row['id'] for row in cursor.fetchall()}

    # Get ALL players who played this season (with their team_id)
    cursor.execute("""
        SELECT DISTINCT ps.player_id, ps.team_id
        FROM player_season_stats ps
        WHERE ps.season_year = ? AND ps.gp >= 1
        ORDER BY ps.pts DESC
    """, (season,))
    players = [(row['player_id'], row['team_id']) for row in cursor.fetchall()]
    print(f"Collecting game logs for {len(players)} players (season {season_str})...")

    total_inserted = 0
    for idx, (player_id, default_team_id) in enumerate(players):
        try:
            log = playergamelog.PlayerGameLog(player_id=player_id, season=season_str)
            df = log.get_data_frames()[0]

            if len(df) == 0:
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

                # Resolve team_id from matchup (e.g. "OKC vs. ORL" -> OKC)
                matchup = row.get('MATCHUP', '')
                team_abbr = matchup.split(' ')[0] if matchup else ''
                team_id = abbr_to_id.get(team_abbr, default_team_id)

                cursor.execute('''
                    INSERT OR IGNORE INTO player_game_stats
                    (player_id, team_id, game_id, season_year, game_date, matchup, wl,
                     min, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct,
                     ftm, fta, ft_pct, oreb, dreb, reb,
                     ast, stl, blk, tov, pf, pts, plus_minus, game_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (player_id, team_id, row.get('Game_ID'), season,
                      row.get('GAME_DATE'), row.get('MATCHUP', ''), row.get('WL'),
                      safe_float(row.get('MIN')),
                      fgm, fga, safe_float(row.get('FG_PCT')),
                      safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                      ftm, fta, safe_float(row.get('FT_PCT')),
                      oreb, dreb, safe_float(row.get('REB')),
                      ast, stl, blk, tov, pf, pts,
                      safe_float(row.get('PLUS_MINUS')), game_score))
                total_inserted += 1

            time.sleep(DELAY)
        except Exception as e:
            if 'rate' in str(e).lower() or '429' in str(e):
                print(f"  Rate limited, waiting 30s...")
                time.sleep(30)
            pass

        if (idx + 1) % 20 == 0:
            conn.commit()
            print(f"  {idx+1}/{len(players)} players done... ({total_inserted} game rows)")

    conn.commit()
    conn.close()
    print(f"\nDone! Inserted {total_inserted} player game stat rows.")


if __name__ == '__main__':
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    collect(year)
