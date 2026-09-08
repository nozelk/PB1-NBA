import sqlite3
import json

conn = sqlite3.connect('nba.db')
cursor = conn.cursor()


with open('files/first_last_year_of_player.json', 'r', encoding='utf-8') as f:
    first_last_data = json.load(f)


with open('files/curr_top_50.json', 'r', encoding='utf-8') as f:
    curr_top_50 = json.load(f)


with open('files/curr_top_50_stats.json', 'r', encoding='utf-8') as f:
    stats_data = json.load(f)


for player_name in curr_top_50:
    if player_name in first_last_data:

        image_path = f"players/{player_name.replace(' ', '_').replace('.', '').replace('č', 'c').replace('ć', 'c')}.png"
        
        cursor.execute('''
            INSERT OR IGNORE INTO players (name, first_year, last_year, image_path)
            VALUES (?, ?, ?, ?)
        ''', (
            player_name,
            int(first_last_data[player_name]["First"]),
            int(first_last_data[player_name]["Last"]),
            image_path
        ))


conn.commit()


for player_name, years_data in stats_data.items():

    cursor.execute('SELECT id FROM players WHERE name = ?', (player_name,))
    player_id = cursor.fetchone()[0]
    

    for year, stats in years_data.items():
        cursor.execute('''
            INSERT INTO player_stats (
                player_id, year, FGM, FGA, FG_percent, FTM, FTA, FT_percent,
                FG3M, FG3A, FG3_percent, OREB, DREB, REB, AST, PF, STL, TOV, BLK, PTS, SALARY
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id,
            int(year),
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
            stats.get("PTS", 0),
            stats.get("SALARY", 0)
        ))


conn.commit()
conn.close()