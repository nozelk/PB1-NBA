import json
from nba_api.stats.endpoints import teamyearbyyearstats

teams_data_by_years = {}

with open("files/teams.json", "r", encoding="utf-8") as f:
  
    teams = json.load(f)
    for team in teams:
        team_id = team['id']
        team_name = team['full_name']
        team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
        team_stats_df = team_stats.get_data_frames()[0]
        
        team_stats_df_filtered = team_stats_df[team_stats_df['YEAR'].str[:4].astype(int) > 2003]
        
        team_stats_dict = team_stats_df_filtered.to_dict(orient='records')
        teams_data_by_years[team_name] = {}
        for row in team_stats_dict:
            season = row['YEAR'].split("-")[0]
            teams_data_by_years[team_name][season] = {
                "WIN%": row["WIN_PCT"],
                "FGM": row["FGM"],
                "FGA": row["FGA"],
                "FG%": row["FG_PCT"],
                "FG3M": row["FG3M"],
                "FG3A": row["FG3A"],
                "FG3%": row["FG3_PCT"],
                "FTM": row["FTM"],
                "FTA": row["FTA"],
                "FT%": row["FT_PCT"],
                "OREB": row["OREB"],
                "DREB": row["DREB"],
                "REB": row["REB"],
                "AST": row["AST"],
                "PF": row["PF"],
                "STL": row["STL"],
                "TOV": row["TOV"],
                "BLK": row["BLK"],
                "PTS": row["PTS"],
            }

with open("files/teams_data_by_years_2004.json", 'w', encoding="utf-8") as j_f:
    json.dump(teams_data_by_years, j_f, indent=4)
