import json
from nba_api.stats.static import teams

all_teams = teams.get_teams()

with open('files/teams.json', 'w', encoding="utf-8") as f:
    json.dump(all_teams, f, indent=4)