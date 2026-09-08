#it takes very long to collect all the data so you shouldn't delete already collected data

import requests
import re
import json

with open("files/teams_just_id_name.json", "r", encoding="utf-8") as f:
    id_name = json.load(f)

with open("files/teams_salaries_per_year.json", "w", encoding="utf-8") as ft:
    with open("files/players_salaries_per_year.json" , "w", encoding="utf-8") as fp:
        with open("files/rosters_per_year.json" , "w", encoding="utf-8") as fr:
            dict_teams = {}
            dict_players = {}
            roster = {}
            names = set()
            for years in range(2023, 2003, -1):
                print(f"{years}-{years + 1}")
                for team in id_name.values():
                    if team not in roster.keys():
                        roster[team] = {}

                    team_ = team.replace(" ", "_").lower()
                    if years == 2023:
                        url = f"https://hoopshype.com/salaries/{team_}/"
                    else:
                        url = f"https://hoopshype.com/salaries/{team_}/{years}-{years + 1}/"
                    req = requests.get(url)
                    page = req.text

                    Team_Payroll_pattern = r'<a href="https://hoopshype.com/salaries/.*?">.*?<\/a>\s*Team Payroll:\s*<span>(.*?)<\/span>'
                    Team_Payroll = re.search(Team_Payroll_pattern, page, re.DOTALL).group(1)
                    if Team_Payroll == "":
                        continue
                    Team_Payroll = int(Team_Payroll[1:].replace(",",""))

                    Team_Payroll_Rank_pattern = r'<a href="https://hoopshype.com/salaries/.*?">.*?<\/a>\s*Team Payroll Rank:\s*<span>(.*?)<\/span>'
                    Team_Payroll_Rank = re.search(Team_Payroll_Rank_pattern, page, re.DOTALL).group(1)



                    if team not in dict_teams.keys():
                        dict_teams[team] = {f"{years}" : {"Payroll Rank" : int(Team_Payroll_Rank), "Payroll": Team_Payroll}}
                    if f"{years - 1}-{years}" not in dict_teams[team].keys():
                        dict_teams[team][f"{years}" ] = {"Payroll Rank" : int(Team_Payroll_Rank), "Payroll": Team_Payroll}

                    players_patteren = r'<table class="hh-salaries-team-table hh-salaries-table-sortable responsive">.*?</table>'
                    players_tab = re.findall(players_patteren, page, re.DOTALL)[0]

                    tr = re.findall(r"<tr>.*?</tr>",players_tab,re.DOTALL)[:-1]

                    for i in tr:
                        try:
                            name = re.search(r'<a href="https://hoopshype.com/player/.*?>(.*?)</a>',i,re.DOTALL).group(1).strip().replace("&#039;","'")

                        except AttributeError:
                            name = re.search(r'<td class="name">(.*?)</td>',i,re.DOTALL).group(1).strip()
                        salary = re.findall(r'<td style="color:.*?>(.*?)</td>', i,re.DOTALL)[0].strip()[1:].replace(",","")

                        if name == "" or salary == "":
                            continue  


                        if f"{years}" not in roster[team].keys():
                            roster[team][f"{years}"] = {}
                        if name not in roster[team][f"{years}"].keys():
                            roster[team][f"{years}"][name] = {"Salary" : salary}


                        
                        
                        
                        
                        

                        if name not in dict_players.keys():
                            dict_players[name] = {f"{years}" : {"Team" : team, "Salary" : salary}}
                        if f"{years}" not in dict_players[name].keys():
                            dict_players[name][f"{years}"] = {"Team" : team, "Salary" : salary}
                        #print(name)
                        #print(url)


            json.dump(dict_players, fp, indent=4)  
            json.dump(dict_teams, ft, indent=4)
            json.dump(roster, fr, indent=4)  


