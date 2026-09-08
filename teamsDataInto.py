import sqlite3
import json

conn = sqlite3.connect('nba.db')
cursor = conn.cursor()

# 1. Uvoz teams.json
with open('files/teams.json', 'r') as f:
    teams = json.load(f)

for team in teams:
    logo_path = f"logos/{team['full_name'].replace(' ', '_')}.png"
    cursor.execute('''
        INSERT OR IGNORE INTO teams 
        (id, full_name, logo_path, abbreviation, city, state, year_founded)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        team['id'],
        team['full_name'],
        logo_path,
        team['abbreviation'],
        team['city'],
        team['state'],
        team['year_founded']
    ))

# 2. Uvoz team_stats (osnovna statistika)
with open('files/teams_data_by_years_2004.json', 'r') as f:
    team_stats = json.load(f)

for team_name, years_data in team_stats.items():
    cursor.execute('SELECT id FROM teams WHERE full_name = ?', (team_name,))
    team_id = cursor.fetchone()[0]
    
    for year, stats in years_data.items():
        cursor.execute('''
            INSERT INTO team_stats (
                team_id, year, WIN_percent, FGM, FGA, FG_percent,
                FTM, FTA, FT_percent, FG3M, FG3A, FG3_percent,
                OREB, DREB, REB, AST, PF, STL, TOV, BLK, PTS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            team_id,
            int(year),
            stats.get("WIN%", 0),
            stats.get("FGM", 0),
            stats.get("FGA", 0),
            stats.get("FG%", 0),
            stats.get("FTM", 0),
            stats.get("FTA", 0),
            stats.get("FT%", 0),
            stats.get("FG3M", 0),
            stats.get("FG3A", 0),
            stats.get("FG3%", 0),
            stats.get("OREB", 0),
            stats.get("DREB", 0),
            stats.get("REB", 0),
            stats.get("AST", 0),
            stats.get("PF", 0),
            stats.get("STL", 0),
            stats.get("TOV", 0),
            stats.get("BLK", 0),
            stats.get("PTS", 0)
        ))

# 3. Uvoz plač (rosters_per_year.json)
with open('files/rosters_per_year.json', 'r') as f:
    rosters = json.load(f)

for team_name, years_data in rosters.items():
    cursor.execute('SELECT id FROM teams WHERE full_name = ?', (team_name,))
    team_id = cursor.fetchone()[0]
    
    for year, players in years_data.items():
        for player_name, salary_info in players.items():
            cursor.execute('SELECT id FROM players WHERE name = ?', (player_name,))
            player_row = cursor.fetchone()
            if player_row:
                player_id = player_row[0]
                cursor.execute('''
                    INSERT INTO salaries (player_id, team_id, year, salary)
                    VALUES (?, ?, ?, ?)
                ''', (player_id, team_id, int(year), int(salary_info["Salary"])))

# 4. Uvoz payroll podatkov (teams_salaries_per_year.json)
with open('files/teams_salaries_per_year.json', 'r') as f:
    payrolls = json.load(f)

for team_name, years_data in payrolls.items():
    cursor.execute('SELECT id FROM teams WHERE full_name = ?', (team_name,))
    team_id = cursor.fetchone()[0]
    
    for year, data in years_data.items():
        cursor.execute('''
            UPDATE team_stats
            SET payroll = ?, payroll_rank = ?
            WHERE team_id = ? AND year = ?
        ''', (data["Payroll"], data["Payroll Rank"], team_id, int(year)))

conn.commit()
conn.close()