import json

teams_name = []

with open("files/teams_just_id_name.json", "r", encoding="utf-8") as f:
    teams = json.load(f)
with open("files/teams_data_by_years_2004.json", "r", encoding="utf-8") as f_t:
    data = json.load(f_t)

for name in teams.values():
    teams_name.append(name)

print(teams_name)
teams_sums_per_year = {}
teams_avg_per_year = {}
teams_min_max_per_year = {}
teams_max_per_year = {}
teams_min_per_year = {}

for year in range(2004, 2024):
    year = str(year)
    for team in teams_name:
        if year not in teams_sums_per_year.keys():
            teams_sums_per_year[year] = {
                "WIN%": data[team][year]["WIN%"],
                "FGM": data[team][year]["FGM"],
                "FGA": data[team][year]["FGA"],
                "FG%": data[team][year]["FG%"],
                "FG3M": data[team][year]["FG3M"],
                "FG3A": data[team][year]["FG3A"],
                "FG3%": data[team][year]["FG3%"],
                "FTM": data[team][year]["FTM"],
                "FTA": data[team][year]["FTA"],
                "FT%": data[team][year]["FT%"],
                "OREB": data[team][year]["OREB"],
                "DREB": data[team][year]["DREB"],
                "REB": data[team][year]["REB"],
                "AST": data[team][year]["AST"],
                "PF": data[team][year]["PF"],
                "STL": data[team][year]["STL"],
                "TOV": data[team][year]["TOV"],
                "BLK": data[team][year]["BLK"],
                "PTS": data[team][year]["PTS"]
            }
            teams_avg_per_year[year] = {}
            teams_min_max_per_year[year] = {
                "WIN%": [data[team][year]["WIN%"]],
                "FGM":  [data[team][year]["FGM"]],
                "FGA":  [data[team][year]["FGA"]],
                "FG%":  [data[team][year]["FG%"]],
                "FG3M": [data[team][year]["FG3M"]],
                "FG3A": [data[team][year]["FG3A"]],
                "FG3%": [data[team][year]["FG3%"]],
                "FTM":  [data[team][year]["FTM"]],
                "FTA":  [data[team][year]["FTA"]],
                "FT%":  [data[team][year]["FT%"]],
                "OREB": [data[team][year]["OREB"]],
                "DREB": [data[team][year]["DREB"]],
                "REB":  [data[team][year]["REB"]],
                "AST":  [data[team][year]["AST"]],
                "PF":   [data[team][year]["PF"]],
                "STL":  [data[team][year]["STL"]],
                "TOV":  [data[team][year]["TOV"]],
                "BLK":  [data[team][year]["BLK"]],
                "PTS":  [data[team][year]["PTS"]]
            }
            teams_max_per_year[year] = {}
            teams_min_per_year[year] = {}
        else:
            teams_sums_per_year[year]["WIN%"] += data[team][year]["WIN%"]
            teams_sums_per_year[year]["FGM"]  += data[team][year]["FGM"]
            teams_sums_per_year[year]["FGA"]  += data[team][year]["FGA"]
            teams_sums_per_year[year]["FG%"]  += data[team][year]["FG%"]
            teams_sums_per_year[year]["FG3M"] += data[team][year]["FG3M"]
            teams_sums_per_year[year]["FG3A"] += data[team][year]["FG3A"]
            teams_sums_per_year[year]["FG3%"] += data[team][year]["FG3%"]
            teams_sums_per_year[year]["FTM"]  += data[team][year]["FTM"]
            teams_sums_per_year[year]["FTA"]  += data[team][year]["FTA"]
            teams_sums_per_year[year]["FT%"]  += data[team][year]["FT%"]
            teams_sums_per_year[year]["OREB"] += data[team][year]["OREB"]
            teams_sums_per_year[year]["DREB"] += data[team][year]["DREB"]
            teams_sums_per_year[year]["REB"]  += data[team][year]["REB"]
            teams_sums_per_year[year]["AST"]  += data[team][year]["AST"]
            teams_sums_per_year[year]["PF"]   += data[team][year]["PF"]
            teams_sums_per_year[year]["STL"]  += data[team][year]["STL"]
            teams_sums_per_year[year]["TOV"]  += data[team][year]["TOV"]
            teams_sums_per_year[year]["BLK"]  += data[team][year]["BLK"]
            teams_sums_per_year[year]["PTS"]  += data[team][year]["PTS"]
            
            teams_min_max_per_year[year]["WIN%"].append((data[team][year]["WIN%"]))
            teams_min_max_per_year[year]["FGM"].append((data[team][year]["FGM"]))
            teams_min_max_per_year[year]["FGA"].append((data[team][year]["FGA"]))
            teams_min_max_per_year[year]["FG%"].append((data[team][year]["FG%"]))
            teams_min_max_per_year[year]["FG3M"].append((data[team][year]["FG3M"]))
            teams_min_max_per_year[year]["FG3A"].append((data[team][year]["FG3A"]))
            teams_min_max_per_year[year]["FG3%"].append((data[team][year]["FG3%"]))
            teams_min_max_per_year[year]["FTM"].append((data[team][year]["FTM"]))
            teams_min_max_per_year[year]["FTA"].append((data[team][year]["FTA"]))
            teams_min_max_per_year[year]["FT%"].append((data[team][year]["FT%"]))
            teams_min_max_per_year[year]["OREB"].append((data[team][year]["OREB"]))
            teams_min_max_per_year[year]["DREB"].append((data[team][year]["DREB"]))
            teams_min_max_per_year[year]["REB"].append((data[team][year]["REB"]))
            teams_min_max_per_year[year]["AST"].append((data[team][year]["AST"]))
            teams_min_max_per_year[year]["PF"].append((data[team][year]["PF"]))
            teams_min_max_per_year[year]["STL"].append((data[team][year]["STL"]))
            teams_min_max_per_year[year]["TOV"].append((data[team][year]["TOV"]))
            teams_min_max_per_year[year]["BLK"].append((data[team][year]["BLK"]))
            teams_min_max_per_year[year]["PTS"].append((data[team][year]["PTS"]))

        if team == 'Charlotte Hornets':
            teams_avg_per_year[year]["WIN%"] = round(teams_sums_per_year[year]["WIN%"] / 30, 3)
            teams_avg_per_year[year]["FGM"]  = round(teams_sums_per_year[year]["FGM"]  / 30)
            teams_avg_per_year[year]["FGA"]  = round(teams_sums_per_year[year]["FGA"]  / 30)
            teams_avg_per_year[year]["FG%"]  = round(teams_sums_per_year[year]["FG%"]  / 30, 3)
            teams_avg_per_year[year]["FG3M"] = round(teams_sums_per_year[year]["FG3M"] / 30)
            teams_avg_per_year[year]["FG3A"] = round(teams_sums_per_year[year]["FG3A"] / 30)
            teams_avg_per_year[year]["FG3%"] = round(teams_sums_per_year[year]["FG3%"] / 30, 3)
            teams_avg_per_year[year]["FTM"]  = round(teams_sums_per_year[year]["FTM"]  / 30)
            teams_avg_per_year[year]["FTA"]  = round(teams_sums_per_year[year]["FTA"]  / 30)
            teams_avg_per_year[year]["FT%"]  = round(teams_sums_per_year[year]["FT%"]  / 30, 3)
            teams_avg_per_year[year]["OREB"] = round(teams_sums_per_year[year]["OREB"] / 30)
            teams_avg_per_year[year]["DREB"] = round(teams_sums_per_year[year]["DREB"] / 30)
            teams_avg_per_year[year]["REB"]  = round(teams_sums_per_year[year]["REB"]  / 30)
            teams_avg_per_year[year]["AST"]  = round(teams_sums_per_year[year]["AST"]  / 30)
            teams_avg_per_year[year]["PF"]   = round(teams_sums_per_year[year]["PF"]   / 30)
            teams_avg_per_year[year]["STL"]  = round(teams_sums_per_year[year]["STL"]  / 30)
            teams_avg_per_year[year]["TOV"]  = round(teams_sums_per_year[year]["TOV"]  / 30)
            teams_avg_per_year[year]["BLK"]  = round(teams_sums_per_year[year]["BLK"]  / 30)
            teams_avg_per_year[year]["PTS"]  = round(teams_sums_per_year[year]["PTS"]  / 30)

            teams_max_per_year[year]["WIN%"] =  max(teams_min_max_per_year[year]["WIN%"])
            teams_max_per_year[year]["FGM"]  =  max(teams_min_max_per_year[year]["FGM"])
            teams_max_per_year[year]["FGA"]  =  max(teams_min_max_per_year[year]["FGA"])
            teams_max_per_year[year]["FG%"]  =  max(teams_min_max_per_year[year]["FG%"])
            teams_max_per_year[year]["FG3M"] =  max(teams_min_max_per_year[year]["FG3M"])
            teams_max_per_year[year]["FG3A"] =  max(teams_min_max_per_year[year]["FG3A"])
            teams_max_per_year[year]["FG3%"] =  max(teams_min_max_per_year[year]["FG3%"])
            teams_max_per_year[year]["FTM"]  =  max(teams_min_max_per_year[year]["FTM"])
            teams_max_per_year[year]["FTA"]  =  max(teams_min_max_per_year[year]["FTA"])
            teams_max_per_year[year]["FT%"]  =  max(teams_min_max_per_year[year]["FT%"])
            teams_max_per_year[year]["OREB"] =  max(teams_min_max_per_year[year]["OREB"])
            teams_max_per_year[year]["DREB"] =  max(teams_min_max_per_year[year]["DREB"])
            teams_max_per_year[year]["REB"]  =  max(teams_min_max_per_year[year]["REB"])
            teams_max_per_year[year]["AST"]  =  max(teams_min_max_per_year[year]["AST"])
            teams_max_per_year[year]["PF"]   =  max(teams_min_max_per_year[year]["PF"])
            teams_max_per_year[year]["STL"]  =  max(teams_min_max_per_year[year]["STL"])
            teams_max_per_year[year]["TOV"]  =  max(teams_min_max_per_year[year]["TOV"])
            teams_max_per_year[year]["BLK"]  =  max(teams_min_max_per_year[year]["BLK"])
            teams_max_per_year[year]["PTS"]  =  max(teams_min_max_per_year[year]["PTS"])

            teams_min_per_year[year]["WIN%"] =  min(teams_min_max_per_year[year]["WIN%"])
            teams_min_per_year[year]["FGM"]  =  min(teams_min_max_per_year[year]["FGM"])
            teams_min_per_year[year]["FGA"]  =  min(teams_min_max_per_year[year]["FGA"])
            teams_min_per_year[year]["FG%"]  =  min(teams_min_max_per_year[year]["FG%"])
            teams_min_per_year[year]["FG3M"] =  min(teams_min_max_per_year[year]["FG3M"])
            teams_min_per_year[year]["FG3A"] =  min(teams_min_max_per_year[year]["FG3A"])
            teams_min_per_year[year]["FG3%"] =  min(teams_min_max_per_year[year]["FG3%"])
            teams_min_per_year[year]["FTM"]  =  min(teams_min_max_per_year[year]["FTM"])
            teams_min_per_year[year]["FTA"]  =  min(teams_min_max_per_year[year]["FTA"])
            teams_min_per_year[year]["FT%"]  =  min(teams_min_max_per_year[year]["FT%"])
            teams_min_per_year[year]["OREB"] =  min(teams_min_max_per_year[year]["OREB"])
            teams_min_per_year[year]["DREB"] =  min(teams_min_max_per_year[year]["DREB"])
            teams_min_per_year[year]["REB"]  =  min(teams_min_max_per_year[year]["REB"])
            teams_min_per_year[year]["AST"]  =  min(teams_min_max_per_year[year]["AST"])
            teams_min_per_year[year]["PF"]   =  min(teams_min_max_per_year[year]["PF"])
            teams_min_per_year[year]["STL"]  =  min(teams_min_max_per_year[year]["STL"])
            teams_min_per_year[year]["TOV"]  =  min(teams_min_max_per_year[year]["TOV"])
            teams_min_per_year[year]["BLK"]  =  min(teams_min_max_per_year[year]["BLK"])
            teams_min_per_year[year]["PTS"]  =  min(teams_min_max_per_year[year]["PTS"])



with open("files/teams_data_by_years_sum_2004.json", 'w', encoding="utf-8") as j_r:
    json.dump(teams_sums_per_year, j_r, indent=4)

with open("files/teams_data_by_years_avg_2004.json", 'w', encoding="utf-8") as j_t:
    json.dump(teams_avg_per_year, j_t, indent=4)

with open("files/teams_data_by_years_max_2004.json", 'w', encoding="utf-8") as j_z:
    json.dump(teams_max_per_year, j_z, indent=4)

with open("files/teams_data_by_years_min_2004.json", 'w', encoding="utf-8") as j_g:
    json.dump(teams_min_per_year, j_g, indent=4)