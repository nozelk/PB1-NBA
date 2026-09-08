"""
Master data collector - runs all collection scripts in order.
Usage: python collect_all.py [--seasons 2004-2024]
"""
import sys
import os
import time
import json
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, init_db

# nba_api imports
from nba_api.stats.static import teams as nba_teams
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import (
    teamyearbyyearstats,
    teamdetails,
    teamgamelog,
    commonteamroster,
    commonplayerinfo,
    playercareerstats,
    playergamelog,
    playerawards,
    leaguedashplayerstats,
    leaguedashteamstats,
)

from datetime import datetime

SEASON_START = 2004
# Current season: if we're before October, current season started last year
_now = datetime.now()
SEASON_END = _now.year if _now.month >= 10 else _now.year - 1
DELAY = 1.5  # seconds between API calls to avoid rate limiting


def season_str(year):
    """Convert 2023 -> '2023-24'"""
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


# ============================================================
# 1. TEAMS
# ============================================================
def collect_teams():
    print("\n=== Collecting Teams ===")
    conn = get_db()
    cursor = conn.cursor()
    
    all_teams = nba_teams.get_teams()
    
    for team in all_teams:
        # Get team details for arena, owner, coach etc
        try:
            details = teamdetails.TeamDetails(team_id=team['id'])
            bg = details.team_background.get_data_frame()
            if len(bg) > 0:
                row = bg.iloc[0]
                arena = row.get('ARENA', '')
                owner = row.get('OWNER', '')
                gm = row.get('GENERALMANAGER', '')
            else:
                arena = owner = gm = ''
            time.sleep(DELAY)
        except Exception as e:
            print(f"  Warning: Could not get details for {team['full_name']}: {e}")
            arena = owner = gm = ''
        
        logo_path = f"logos/{team['full_name'].replace(' ', '_')}.png"
        
        # Determine conference/division
        _TEAM_DIVISIONS = {
            # Eastern – Atlantic
            'Boston Celtics': ('Eastern', 'Atlantic'),
            'Brooklyn Nets': ('Eastern', 'Atlantic'),
            'New York Knicks': ('Eastern', 'Atlantic'),
            'Philadelphia 76ers': ('Eastern', 'Atlantic'),
            'Toronto Raptors': ('Eastern', 'Atlantic'),
            # Eastern – Central
            'Chicago Bulls': ('Eastern', 'Central'),
            'Cleveland Cavaliers': ('Eastern', 'Central'),
            'Detroit Pistons': ('Eastern', 'Central'),
            'Indiana Pacers': ('Eastern', 'Central'),
            'Milwaukee Bucks': ('Eastern', 'Central'),
            # Eastern – Southeast
            'Atlanta Hawks': ('Eastern', 'Southeast'),
            'Charlotte Hornets': ('Eastern', 'Southeast'),
            'Miami Heat': ('Eastern', 'Southeast'),
            'Orlando Magic': ('Eastern', 'Southeast'),
            'Washington Wizards': ('Eastern', 'Southeast'),
            # Western – Northwest
            'Denver Nuggets': ('Western', 'Northwest'),
            'Minnesota Timberwolves': ('Western', 'Northwest'),
            'Oklahoma City Thunder': ('Western', 'Northwest'),
            'Portland Trail Blazers': ('Western', 'Northwest'),
            'Utah Jazz': ('Western', 'Northwest'),
            # Western – Pacific
            'Golden State Warriors': ('Western', 'Pacific'),
            'Los Angeles Clippers': ('Western', 'Pacific'),
            'Los Angeles Lakers': ('Western', 'Pacific'),
            'Phoenix Suns': ('Western', 'Pacific'),
            'Sacramento Kings': ('Western', 'Pacific'),
            # Western – Southwest
            'Dallas Mavericks': ('Western', 'Southwest'),
            'Houston Rockets': ('Western', 'Southwest'),
            'Memphis Grizzlies': ('Western', 'Southwest'),
            'New Orleans Pelicans': ('Western', 'Southwest'),
            'San Antonio Spurs': ('Western', 'Southwest'),
        }
        conference, division = _TEAM_DIVISIONS.get(team['full_name'], ('Western', ''))
        
        cursor.execute('''
            INSERT OR REPLACE INTO teams (id, full_name, abbreviation, nickname, city, state,
                conference, division, year_founded, arena, owner, gm, logo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (team['id'], team['full_name'], team['abbreviation'], team['nickname'],
              team['city'], team['state'], conference, division,
              team['year_founded'], arena, owner, gm, logo_path))
        
        print(f"  ✓ {team['full_name']}")
    
    conn.commit()
    conn.close()
    print(f"  Total: {len(all_teams)} teams")


# ============================================================
# 2. TEAM SEASON STATS
# ============================================================
def collect_team_season_stats():
    print("\n=== Collecting Team Season Stats ===")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, full_name FROM teams")
    teams = cursor.fetchall()
    
    for team in teams:
        team_id, team_name = team['id'], team['full_name']
        try:
            stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
            df = stats.get_data_frames()[0]
            
            for _, row in df.iterrows():
                year = int(row['YEAR'].split('-')[0])
                if year < SEASON_START or year > SEASON_END:
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO team_season_stats 
                    (team_id, season_year, wins, losses, win_pct, fgm, fga, fg_pct,
                     fg3m, fg3a, fg3_pct, ftm, fta, ft_pct, oreb, dreb, reb,
                     ast, stl, blk, tov, pf, pts)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (team_id, year, safe_int(row.get('WINS')), safe_int(row.get('LOSSES')),
                      safe_float(row.get('WIN_PCT')),
                      safe_float(row.get('FGM')), safe_float(row.get('FGA')), safe_float(row.get('FG_PCT')),
                      safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                      safe_float(row.get('FTM')), safe_float(row.get('FTA')), safe_float(row.get('FT_PCT')),
                      safe_float(row.get('OREB')), safe_float(row.get('DREB')), safe_float(row.get('REB')),
                      safe_float(row.get('AST')), safe_float(row.get('STL')), safe_float(row.get('BLK')),
                      safe_float(row.get('TOV')), safe_float(row.get('PF')), safe_float(row.get('PTS'))))
            
            print(f"  ✓ {team_name}")
            time.sleep(DELAY)
        except Exception as e:
            print(f"  ✗ {team_name}: {e}")
    
    conn.commit()
    conn.close()


# ============================================================
# 3. GAMES (Team Game Logs)
# ============================================================
def collect_games():
    print("\n=== Collecting Games ===")
    conn = get_db()
    cursor = conn.cursor()
    
    # Build abbreviation -> team_id lookup
    cursor.execute("SELECT id, abbreviation, full_name FROM teams")
    teams = cursor.fetchall()
    abbrev_to_id = {t['abbreviation']: t['id'] for t in teams}
    
    for team in teams:
        team_id = team['id']
        team_name = team['full_name']
        
        for year in range(SEASON_START, SEASON_END + 1):
            try:
                log = teamgamelog.TeamGameLog(team_id=team_id, season=season_str(year))
                df = log.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    game_id = row['Game_ID']
                    matchup = row.get('MATCHUP', '')
                    
                    # Parse opponent from matchup (e.g., "LAL vs. BOS" or "LAL @ BOS")
                    opponent_id = None
                    if matchup:
                        parts = matchup.replace(' vs. ', ' @ ').split(' @ ')
                        if len(parts) == 2:
                            opp_abbrev = parts[1].strip()
                            opponent_id = abbrev_to_id.get(opp_abbrev)
                    
                    # Get opponent points from plus_minus and pts
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
                    ''', (game_id, year, row.get('GAME_DATE'), matchup, team_id, opponent_id,
                          row.get('WL'), pts, opp_pts,
                          safe_float(row.get('FGM')), safe_float(row.get('FGA')), safe_float(row.get('FG_PCT')),
                          safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                          safe_float(row.get('FTM')), safe_float(row.get('FTA')), safe_float(row.get('FT_PCT')),
                          safe_float(row.get('OREB')), safe_float(row.get('DREB')), safe_float(row.get('REB')),
                          safe_float(row.get('AST')), safe_float(row.get('STL')), safe_float(row.get('BLK')),
                          safe_float(row.get('TOV')), safe_float(row.get('PF')),
                          plus_minus, 'Regular Season'))
                
                time.sleep(DELAY)
            except Exception as e:
                print(f"  ✗ {team_name} {year}: {e}")
        
        print(f"  ✓ {team_name} (all seasons)")
        conn.commit()
    
    conn.close()


# ============================================================
# 4. PLAYERS + PLAYER SEASON STATS
# ============================================================
def collect_players_and_stats():
    print("\n=== Collecting Players & Season Stats ===")
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all players who appear in game logs or use leaguedashplayerstats
    collected_player_ids = set()
    
    for year in range(SEASON_START, SEASON_END + 1):
        print(f"  Season {year}-{year+1}...")
        try:
            league_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season_str(year),
                per_mode_detailed='Totals'
            )
            df = league_stats.get_data_frames()[0]
            
            for _, row in df.iterrows():
                player_id = int(row['PLAYER_ID'])
                team_id = safe_int(row.get('TEAM_ID'))
                
                # Insert player if not exists
                if player_id not in collected_player_ids:
                    player_name = row.get('PLAYER_NAME', '')
                    parts = player_name.split(' ', 1)
                    first = parts[0] if parts else ''
                    last = parts[1] if len(parts) > 1 else ''
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO players (id, first_name, last_name, display_name)
                        VALUES (?, ?, ?, ?)
                    ''', (player_id, first, last, player_name))
                    collected_player_ids.add(player_id)
                
                # Insert season stats
                cursor.execute('''
                    INSERT OR REPLACE INTO player_season_stats
                    (player_id, team_id, season_year, age, gp, gs, min,
                     fgm, fga, fg_pct, fg3m, fg3a, fg3_pct,
                     ftm, fta, ft_pct, oreb, dreb, reb,
                     ast, stl, blk, tov, pf, pts, plus_minus)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (player_id, team_id, year,
                      safe_int(row.get('AGE')), safe_int(row.get('GP')), safe_int(row.get('GS')),
                      safe_float(row.get('MIN')),
                      safe_float(row.get('FGM')), safe_float(row.get('FGA')), safe_float(row.get('FG_PCT')),
                      safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                      safe_float(row.get('FTM')), safe_float(row.get('FTA')), safe_float(row.get('FT_PCT')),
                      safe_float(row.get('OREB')), safe_float(row.get('DREB')), safe_float(row.get('REB')),
                      safe_float(row.get('AST')), safe_float(row.get('STL')), safe_float(row.get('BLK')),
                      safe_float(row.get('TOV')), safe_float(row.get('PF')), safe_float(row.get('PTS')),
                      safe_float(row.get('PLUS_MINUS'))))
            
            conn.commit()
            print(f"    ✓ {len(df)} players")
            time.sleep(DELAY)
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    conn.close()
    print(f"  Total unique players: {len(collected_player_ids)}")


# ============================================================
# 5. PLAYER DETAILS (height, weight, country, draft, etc.)
# ============================================================
def collect_player_details():
    print("\n=== Collecting Player Details ===")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, display_name FROM players WHERE position IS NULL OR country IS NULL")
    players_to_update = cursor.fetchall()
    total = len(players_to_update)
    
    for i, player in enumerate(players_to_update):
        player_id = player['id']
        try:
            info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
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
                      player_id))
            
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{total} players updated...")
                conn.commit()
            
            time.sleep(DELAY)
        except Exception as e:
            print(f"  ✗ Player {player['display_name']}: {e}")
    
    conn.commit()
    conn.close()
    print(f"  ✓ Updated {total} players")


# ============================================================
# 6. PLAYER GAME STATS
# ============================================================
def collect_player_game_stats():
    print("\n=== Collecting Player Game Stats ===")
    conn = get_db()
    cursor = conn.cursor()
    
    # Only collect for players with significant stats (top performers)
    cursor.execute("""
        SELECT DISTINCT player_id FROM player_season_stats 
        WHERE pts > 500 AND gp > 40
        ORDER BY pts DESC
    """)
    player_ids = [row['player_id'] for row in cursor.fetchall()]
    print(f"  Collecting game logs for {len(player_ids)} significant players...")
    
    for idx, player_id in enumerate(player_ids):
        for year in range(SEASON_START, SEASON_END + 1):
            try:
                log = playergamelog.PlayerGameLog(player_id=player_id, season=season_str(year))
                df = log.get_data_frames()[0]
                
                if len(df) == 0:
                    continue
                
                for _, row in df.iterrows():
                    # Calculate GameScore
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
                    
                    game_score = round(pts + 0.4*fgm - 0.7*fga - 0.4*(fta-ftm) + 0.7*oreb + 0.3*dreb + stl + 0.7*ast + 0.7*blk - 0.4*pf - tov, 1)
                    
                    # Parse team_id from matchup
                    matchup = row.get('MATCHUP', '')
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO player_game_stats
                        (player_id, team_id, game_id, season_year, game_date, matchup, wl,
                         min, fgm, fga, fg_pct, fg3m, fg3a, fg3_pct,
                         ftm, fta, ft_pct, oreb, dreb, reb,
                         ast, stl, blk, tov, pf, pts, plus_minus, game_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (player_id, 0, row.get('Game_ID'), year,
                          row.get('GAME_DATE'), matchup, row.get('WL'),
                          safe_float(row.get('MIN')),
                          fgm, fga, safe_float(row.get('FG_PCT')),
                          safe_float(row.get('FG3M')), safe_float(row.get('FG3A')), safe_float(row.get('FG3_PCT')),
                          ftm, fta, safe_float(row.get('FT_PCT')),
                          oreb, dreb, safe_float(row.get('REB')),
                          ast, stl, blk, tov, pf, pts,
                          safe_float(row.get('PLUS_MINUS')), game_score))
                
                time.sleep(DELAY)
            except Exception:
                pass
        
        if (idx + 1) % 10 == 0:
            conn.commit()
            print(f"  {idx+1}/{len(player_ids)} players done...")
    
    conn.commit()
    conn.close()


# ============================================================
# 7. COACHES
# ============================================================
def collect_coaches():
    print("\n=== Collecting Coaches ===")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, full_name FROM teams")
    teams = cursor.fetchall()
    
    for team in teams:
        team_id = team['id']
        try:
            details = teamdetails.TeamDetails(team_id=team_id)
            bg = details.team_background.get_data_frame()
            
            if len(bg) > 0:
                coach_name = bg.iloc[0].get('HEADCOACH', '')
                if coach_name:
                    cursor.execute('INSERT OR IGNORE INTO coaches (name) VALUES (?)', (coach_name,))
                    cursor.execute('SELECT id FROM coaches WHERE name = ?', (coach_name,))
                    coach_id = cursor.fetchone()['id']
                    
                    # Get current year stats from team_season_stats
                    cursor.execute('''
                        SELECT season_year, wins, losses FROM team_season_stats 
                        WHERE team_id = ? ORDER BY season_year DESC LIMIT 1
                    ''', (team_id,))
                    season = cursor.fetchone()
                    if season:
                        cursor.execute('''
                            INSERT OR IGNORE INTO coach_seasons 
                            (coach_id, team_id, season_year, wins, losses, season_type)
                            VALUES (?, ?, ?, ?, ?, 'Regular Season')
                        ''', (coach_id, team_id, season['season_year'], season['wins'], season['losses']))
            
            time.sleep(DELAY)
        except Exception as e:
            print(f"  ✗ {team['full_name']}: {e}")
    
    # Also try to get historical coaches from game logs / manual mapping
    # For comprehensive coach data, we can parse from basketball-reference
    _collect_historical_coaches(conn)
    
    conn.commit()
    conn.close()


def _collect_historical_coaches(conn):
    """Try to collect historical coaches - simplified approach."""
    cursor = conn.cursor()
    
    # Known coaches mapping (major coaches 2004-2024)
    historical = [
        ("Gregg Popovich", 1610612759, 2004, 2024),  # Spurs
        ("Phil Jackson", 1610612747, 2004, 2011),     # Lakers
        ("Erik Spoelstra", 1610612748, 2008, 2024),   # Heat
        ("Steve Kerr", 1610612744, 2014, 2024),       # Warriors
        ("Doc Rivers", 1610612746, 2004, 2013),       # Celtics -> Clippers
        ("Brad Stevens", 1610612738, 2013, 2021),     # Celtics
        ("Rick Carlisle", 1610612742, 2008, 2021),    # Mavericks
        ("Mike Budenholzer", 1610612749, 2018, 2023), # Bucks
        ("Tyronn Lue", 1610612739, 2016, 2018),       # Cavaliers
        ("Tom Thibodeau", 1610612752, 2020, 2024),    # Knicks
        ("Ime Udoka", 1610612745, 2022, 2024),        # Rockets
        ("Jason Kidd", 1610612742, 2021, 2024),       # Mavericks
        ("Joe Mazzulla", 1610612738, 2022, 2024),     # Celtics
        ("Nick Nurse", 1610612761, 2018, 2023),       # Raptors
        ("Monty Williams", 1610612756, 2019, 2023),   # Suns
        ("Mike D'Antoni", 1610612756, 2004, 2008),    # Suns
        ("Quin Snyder", 1610612762, 2014, 2022),      # Jazz
        ("Frank Vogel", 1610612747, 2019, 2022),      # Lakers
        ("LeBron James Coach", 0, 0, 0),              # skip
    ]
    
    for coach_name, team_id, start, end in historical:
        if team_id == 0:
            continue
        cursor.execute('INSERT OR IGNORE INTO coaches (name) VALUES (?)', (coach_name,))
        cursor.execute('SELECT id FROM coaches WHERE name = ?', (coach_name,))
        coach_row = cursor.fetchone()
        if coach_row:
            coach_id = coach_row['id']
            for year in range(start, end + 1):
                cursor.execute('SELECT wins, losses FROM team_season_stats WHERE team_id = ? AND season_year = ?',
                             (team_id, year))
                ts = cursor.fetchone()
                if ts:
                    cursor.execute('''
                        INSERT OR IGNORE INTO coach_seasons 
                        (coach_id, team_id, season_year, wins, losses, season_type)
                        VALUES (?, ?, ?, ?, ?, 'Regular Season')
                    ''', (coach_id, team_id, year, ts['wins'], ts['losses']))


# ============================================================
# 8. ROSTERS
# ============================================================
def collect_rosters():
    print("\n=== Collecting Rosters ===")
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, full_name FROM teams")
    teams = cursor.fetchall()
    
    for team in teams:
        team_id = team['id']
        for year in range(SEASON_START, SEASON_END + 1):
            try:
                roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season_str(year))
                df = roster.get_data_frames()[0]
                
                for _, row in df.iterrows():
                    player_id = int(row['PLAYER_ID'])
                    
                    # Make sure player exists
                    cursor.execute('SELECT id FROM players WHERE id = ?', (player_id,))
                    if not cursor.fetchone():
                        cursor.execute('''
                            INSERT OR IGNORE INTO players (id, display_name, first_name, last_name, position)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (player_id, row.get('PLAYER', ''),
                              row.get('PLAYER', '').split(' ')[0],
                              ' '.join(row.get('PLAYER', '').split(' ')[1:]),
                              row.get('POSITION', '')))
                    
                    cursor.execute('''
                        INSERT OR IGNORE INTO rosters (player_id, team_id, season_year, position, jersey_num)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (player_id, team_id, year,
                          row.get('POSITION', ''), safe_int(row.get('NUM'))))
                
                time.sleep(DELAY)
            except Exception:
                pass
        
        print(f"  ✓ {team['full_name']}")
        conn.commit()
    
    conn.close()


# ============================================================
# 9. AWARDS
# ============================================================
def collect_awards():
    print("\n=== Collecting Player Awards ===")
    conn = get_db()
    cursor = conn.cursor()
    
    # Get significant players
    cursor.execute("""
        SELECT DISTINCT player_id FROM player_season_stats 
        WHERE pts > 800 AND gp > 50
    """)
    player_ids = [row['player_id'] for row in cursor.fetchall()]
    
    for idx, player_id in enumerate(player_ids):
        try:
            a = playerawards.PlayerAwards(player_id=player_id)
            df = a.get_data_frames()[0]
            
            for _, row in df.iterrows():
                desc = row.get('DESCRIPTION', '')
                award_type = row.get('TYPE', '')
                
                # Parse season year 
                season = row.get('SEASON', '')
                year = None
                if season and '-' in str(season):
                    try:
                        year = int(str(season).split('-')[0])
                    except ValueError:
                        pass
                
                cursor.execute('''
                    INSERT OR IGNORE INTO awards (player_id, award_type, season_year, description)
                    VALUES (?, ?, ?, ?)
                ''', (player_id, award_type, year, desc))
            
            time.sleep(DELAY)
        except Exception:
            pass
        
        if (idx + 1) % 50 == 0:
            conn.commit()
            print(f"  {idx+1}/{len(player_ids)} players processed...")
    
    conn.commit()
    conn.close()


# ============================================================
# 10. SALARIES — uses standalone collect_salaries.py
# ============================================================
from collect_salaries import collect_salaries


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("NBA Data Collection Pipeline")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Run collection in order
    steps = [
        ("1/8", "Teams", collect_teams),
        ("2/8", "Team Season Stats", collect_team_season_stats),
        ("3/8", "Players & Season Stats", collect_players_and_stats),
        ("4/8", "Player Details", collect_player_details),
        ("5/8", "Games", collect_games),
        ("6/8", "Rosters", collect_rosters),
        ("7/8", "Coaches", collect_coaches),
        ("8/8", "Salaries", collect_salaries),
    ]
    
    for step_num, step_name, func in steps:
        print(f"\n{'='*60}")
        print(f"Step {step_num}: {step_name}")
        print(f"{'='*60}")
        try:
            func()
        except Exception as e:
            print(f"ERROR in {step_name}: {e}")
            print("Continuing with next step...")
    
    # Optional: run these if you have time (they take long)
    # collect_player_game_stats()
    # collect_awards()
    
    print("\n" + "=" * 60)
    print("DATA COLLECTION COMPLETE!")
    print("=" * 60)
    
    # Print summary
    from database import query_db
    tables = ['teams', 'players', 'team_season_stats', 'player_season_stats', 
              'games', 'rosters', 'coaches', 'coach_seasons', 'salaries', 'awards']
    for table in tables:
        try:
            count = query_db(f"SELECT COUNT(*) as c FROM {table}", one=True)
            print(f"  {table}: {count['c']} rows")
        except:
            print(f"  {table}: 0 rows")
