import json
from nba_api.stats.endpoints import teamyearbyyearstats

teams_stats_list = []

with open("files/teams.json", "r", encoding="utf-8") as f:
    teams = json.load(f)
    for team in teams:
        team_id = team['id']
        team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
        team_stats_df = team_stats.get_data_frames()[0]

        team_stats_dict = team_stats_df.to_dict(orient='records')

        teams_stats_list.append(team_stats_dict)

with open("files/teams_data_by_years.json", 'w', encoding="utf-8") as j_f:
    json.dump(teams_stats_list, j_f, indent=4)

