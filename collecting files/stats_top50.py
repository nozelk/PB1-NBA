import json
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats


with open('files/curr_top_50.json', 'r', encoding="utf-8") as f:
    player_list = json.load(f)

with open("files/players_salaries_per_year.json", "r", encoding="utf-8") as f:
    salaries = json.load(f)

player_stats = {}
for player_name in player_list:
    if player_name == "Luka Dončić": player_name = "Luka Doncic"
    if player_name == "Nikola Jokić": player_name = "Nikola Jokic"

    player_info = players.find_players_by_full_name(player_name)
    if player_name == "Luka Doncic": player_name = "Luka Dončić"
    if player_name == "Nikola Jokic": player_name = "Nikola Jokić"

    player_stats[player_name] = {}
    player_info = player_info[0]
    
    career = playercareerstats.PlayerCareerStats(player_id=player_info['id'])
    career_df = career.get_data_frames()[0]
    stats = career_df.to_dict('records')

    for season in stats:
        if int(season["SEASON_ID"].split("-")[0]) < 2004:
            continue
        if player_name == "Luka Dončić":
            p_n = "Luka Doncic"
        elif player_name == "Nikola Jokić":
            p_n = "Nikola Jokic"
        elif player_name == "Jaren Jackson Jr.":
            p_n = "Jaren Jackson Jr"
        else:
            p_n = player_name
        print(p_n)
        player_stats[player_name][season["SEASON_ID"].split("-")[0]] = {
            "AGE"    : season["PLAYER_AGE"],
            "GP"     : season["GP"],
            "GS"     : season["GS"],
            "MIN"    : season["MIN"],
            "FGM"    : season["FGM"],
            "FGA"    : season["FGA"],
            "FG%"    : season["FG_PCT"],
            "FG3M"   : season["FG3M"],
            "FG3A"   : season["FG3A"],
            "FG3%"   : season["FG3_PCT"],
            "FTM"    : season["FTM"],
            "FTA"    : season["FTA"],
            "FT%"    : season["FT_PCT"],
            "OREB"   : season["OREB"],
            "DREB"   : season["DREB"],
            "REB"    : season["REB"],
            "AST"    : season["AST"],
            "PF"     : season["PF"], 
            "STL"    : season["STL"],
            "TOV"    : season["TOV"],
            "BLK"    : season["BLK"],
            "PTS"    : season["PTS"],
            "SALARY" : int(salaries[p_n][season["SEASON_ID"].split("-")[0]]["Salary"])
        }


with open('files/curr_top_50_stats.json', 'w',encoding="utf-8") as f:
    json.dump(player_stats, f, indent=4, ensure_ascii=False)
