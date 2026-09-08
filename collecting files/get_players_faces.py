import requests
import re
import json

with open("files/teams_just_id_name.json", "r", encoding="utf-8") as f:
    id_name = json.load(f)

for team in id_name.values():
    team_ = team.replace(" ", "_").lower()
    url = f"https://hoopshype.com/salaries/{team_}/"
    req = requests.get(url)
    page = req.text
    
    players_patteren = r'<table class="hh-salaries-team-table hh-salaries-table-sortable responsive">.*?</table>'
    players_tab = re.findall(players_patteren, page, re.DOTALL)[0]

    tr = re.findall(r"<tr>.*?</tr>",players_tab,re.DOTALL)[:-1]

    for i in tr:
        try:
            name = re.search(r'<a href="https://hoopshype.com/player/.*?>(.*?)</a>',i,re.DOTALL).group(1).strip().replace("&#039;","'")

        except AttributeError:
            name = re.search(r'<td class="name">(.*?)</td>',i,re.DOTALL).group(1).strip()
        
        url2 = f"https://hoopshype.com/player/{name.replace(" ","-")}/"
        req2 = requests.get(url2)
        page2 = req2.text
        try:
            picture_match = re.search(r'<div class="player-headshot">.*?<img src="(.*?)" alt.*?</div>', page2, re.IGNORECASE | re.DOTALL).group(1)
            image = "https://cdn.hoopshype.com/i/"
            if not picture_match[:len(image)] == image:
                continue
            img_data = requests.get(picture_match).content
            with open(f"players/{name.replace("'","").replace(" ","_")}.png", "wb") as img_file:
                img_file.write(img_data)
            
        except AttributeError:
            pass
