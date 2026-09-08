import os
import re
import requests
import json

logo_dir = "logos"
if not os.path.exists(logo_dir):
    os.makedirs(logo_dir)

with open("files/teams_just_id_name.json", "r", encoding="utf-8") as f:
    name_id = json.load(f)

for team_id in name_id:
    team_name = name_id[team_id].replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{team_name}"
    req = requests.get(url)
    page = req.text

    img_url_pattern = r'<img .*?alt="{} .*?src="(.*?)"'.format(re.escape(name_id[team_id]))
    img_url = re.search(img_url_pattern, page, re.IGNORECASE).group(1)
    if not img_url.startswith("http"):
        img_url = "https:" + img_url
    img_data = requests.get(img_url).content
    file_name = f"{name_id[team_id]}.png"
    file_path = os.path.join(logo_dir, file_name)
    with open(file_path, "wb") as img_file:
        img_file.write(img_data)
    print("Logo for", name_id[team_id], "saved")