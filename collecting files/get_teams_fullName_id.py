import json

id_name = {}

with open("files/teams.json", "r", encoding="utf-8") as f:
    teams = json.load(f)
    for team in teams:
        id_name[team["id"]] = team["full_name"]

with open("files/teams_just_id_name.json", "w", encoding="utf-8") as f:
    json.dump(id_name, f, indent=4)