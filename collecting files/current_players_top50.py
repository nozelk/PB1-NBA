import pandas as pd
import json
url = 'https://www.basketball-reference.com/leagues/NBA_2024_per_game.html'
tables = pd.read_html(url)
df = tables[0]

df = df[df['Rk'].apply(lambda x: str(x).isnumeric())]
df = df.astype({'PTS': float})

top_50 = df.sort_values('PTS', ascending=False).head(50)

player_names = top_50['Player'].tolist()


with open("files/curr_top_50.json", 'w', encoding="utf-8") as j_g:
    json.dump(player_names, j_g, indent=4, ensure_ascii=False)
