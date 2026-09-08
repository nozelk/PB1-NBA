import json

with open('files/curr_top_50_stats.json', 'r',encoding="utf-8") as f:
    player_list = json.load(f)

first_last = {}

for i in player_list.keys():
    print(i)
    first_last[i] = {"First" : list(player_list[i].keys())[0],"Last" : list(player_list[i].keys())[-1]}


with open('files/first_last_year_of_player.json', "w",encoding="utf-8") as f:
    json.dump(first_last, f, indent=4, ensure_ascii=False)