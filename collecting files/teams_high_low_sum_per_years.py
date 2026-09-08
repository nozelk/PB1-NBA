import json


with open("files/teams_just_id_name.json", "r", encoding="utf-8") as f:
    id_name = json.load(f)

with open("files/teams_data_by_years.json", "r", encoding="utf-8") as f:
    stat = json.load(f)
    donary = dict()
    ddoanry = dict()
    for team in stat:
        for years in team:
            if years["YEAR"] not in donary.keys():
                donary[years["YEAR"]] = {
                                        "WinsMIN": years["WINS"],
                                        "LossesMIN": years["LOSSES"],
                                        "Win PercentMIN": years["WIN_PCT"],
                                        "FGMMIN": years["FGM"],
                                        "FGAMIN": years["FGA"],
                                        "FG_PCTMIN": years["FG_PCT"],
                                        "FG3MMIN": years["FG3M"],
                                        "FG3AMIN": years["FG3A"],
                                        "FG3_PCTMIN": years["FG3_PCT"],
                                        "FTMMIN": years["FTM"],
                                        "FTAMIN": years["FTA"],
                                        "FT_PCTMIN": years["FT_PCT"],
                                        "OREBMIN": years["OREB"],
                                        "DREBMIN": years["DREB"],
                                        "REBMIN": years["REB"],
                                        "ASTMIN": years["AST"],
                                        "PFMIN": years["PF"],
                                        "STLMIN": years["STL"],
                                        "TOVMIN": years["TOV"],
                                        "BLKMIN": years["BLK"],
                                        "PTSMIN": years["PTS"],
                                        "WinsMAX": years["WINS"],
                                        "LossesMAX": years["LOSSES"],
                                        "Win PercentMAX": years["WIN_PCT"],
                                        "FGMMAX": years["FGM"],
                                        "FGAMAX": years["FGA"],
                                        "FG_PCTMAX": years["FG_PCT"],
                                        "FG3MMAX": years["FG3M"],
                                        "FG3AMAX": years["FG3A"],
                                        "FG3_PCTMAX": years["FG3_PCT"],
                                        "FTMMAX": years["FTM"],
                                        "FTAMAX": years["FTA"],
                                        "FT_PCTMAX": years["FT_PCT"],
                                        "OREBMAX": years["OREB"],
                                        "DREBMAX": years["DREB"],
                                        "REBMAX": years["REB"],
                                        "ASTMAX": years["AST"],
                                        "PFMAX": years["PF"],
                                        "STLMAX": years["STL"],
                                        "TOVMAX": years["TOV"],
                                        "BLKMAX": years["BLK"],
                                        "PTSMAX": years["PTS"]
                                        }
                ddoanry[years["YEAR"]] = {
                                        "GP": years["GP"],
                                        "FGM": years["FGM"],
                                        "FGA": years["FGA"],
                                        "FG3M": years["FG3M"],
                                        "FG3A": years["FG3A"],
                                        "FTM": years["FTM"],
                                        "FTA": years["FTA"],
                                        "OREB": years["OREB"],
                                        "DREB": years["DREB"],
                                        "REB": years["REB"],
                                        "AST": years["AST"],
                                        "PF": years["PF"],
                                        "STL": years["STL"],
                                        "TOV": years["TOV"],
                                        "BLK": years["BLK"],
                                        "PTS": years["PTS"],
                                        "NOT" : 1
                }
            else:
                donary[years["YEAR"]]["WinsMIN"] = min(donary[years["YEAR"]]["WinsMIN"], years["WINS"])
                donary[years["YEAR"]]["LossesMIN"] = min(donary[years["YEAR"]]["LossesMIN"], years["LOSSES"])
                donary[years["YEAR"]]["Win PercentMIN"] = min(donary[years["YEAR"]]["Win PercentMIN"], years["WIN_PCT"])
                donary[years["YEAR"]]["FGMMIN"] = min(donary[years["YEAR"]]["FGMMIN"], years["FGM"])
                donary[years["YEAR"]]["FGAMIN"] = min(donary[years["YEAR"]]["FGAMIN"], years["FGA"])
                donary[years["YEAR"]]["FG_PCTMIN"] = min(donary[years["YEAR"]]["FG_PCTMIN"], years["FG_PCT"])
                donary[years["YEAR"]]["FG3MMIN"] = min(donary[years["YEAR"]]["FG3MMIN"], years["FG3M"])
                donary[years["YEAR"]]["FG3AMIN"] = min(donary[years["YEAR"]]["FG3AMIN"], years["FG3A"])
                donary[years["YEAR"]]["FG3_PCTMIN"] = min(donary[years["YEAR"]]["FG3_PCTMIN"], years["FG3_PCT"])
                donary[years["YEAR"]]["FTMMIN"] = min(donary[years["YEAR"]]["FTMMIN"], years["FTM"])
                donary[years["YEAR"]]["FTAMIN"] = min(donary[years["YEAR"]]["FTAMIN"], years["FTA"])
                donary[years["YEAR"]]["FT_PCTMIN"] = min(donary[years["YEAR"]]["FT_PCTMIN"], years["FT_PCT"])
                donary[years["YEAR"]]["OREBMIN"] = min(donary[years["YEAR"]]["OREBMIN"], years["OREB"])
                donary[years["YEAR"]]["DREBMIN"] = min(donary[years["YEAR"]]["DREBMIN"], years["DREB"])
                donary[years["YEAR"]]["REBMIN"] = min(donary[years["YEAR"]]["REBMIN"], years["REB"])
                donary[years["YEAR"]]["ASTMIN"] = min(donary[years["YEAR"]]["ASTMIN"], years["AST"])
                donary[years["YEAR"]]["PFMIN"] = min(donary[years["YEAR"]]["PFMIN"], years["PF"])
                donary[years["YEAR"]]["STLMIN"] = min(donary[years["YEAR"]]["STLMIN"], years["STL"])
                donary[years["YEAR"]]["TOVMIN"] = min(donary[years["YEAR"]]["TOVMIN"], years["TOV"])
                donary[years["YEAR"]]["BLKMIN"] = min(donary[years["YEAR"]]["BLKMIN"], years["BLK"])
                donary[years["YEAR"]]["PTSMIN"] = min(donary[years["YEAR"]]["PTSMIN"], years["PTS"])

                donary[years["YEAR"]]["WinsMAX"] = max(donary[years["YEAR"]]["WinsMAX"], years["WINS"])
                donary[years["YEAR"]]["LossesMAX"] = max(donary[years["YEAR"]]["LossesMAX"], years["LOSSES"])
                donary[years["YEAR"]]["Win PercentMAX"] = max(donary[years["YEAR"]]["Win PercentMAX"], years["WIN_PCT"])
                donary[years["YEAR"]]["FGMMAX"] = max(donary[years["YEAR"]]["FGMMAX"], years["FGM"])
                donary[years["YEAR"]]["FGAMAX"] = max(donary[years["YEAR"]]["FGAMAX"], years["FGA"])
                donary[years["YEAR"]]["FG_PCTMAX"] = max(donary[years["YEAR"]]["FG_PCTMAX"], years["FG_PCT"])
                donary[years["YEAR"]]["FG3MMAX"] = max(donary[years["YEAR"]]["FG3MMAX"], years["FG3M"])
                donary[years["YEAR"]]["FG3AMAX"] = max(donary[years["YEAR"]]["FG3AMAX"], years["FG3A"])
                donary[years["YEAR"]]["FG3_PCTMAX"] = max(donary[years["YEAR"]]["FG3_PCTMAX"], years["FG3_PCT"])
                donary[years["YEAR"]]["FTMMAX"] = max(donary[years["YEAR"]]["FTMMAX"], years["FTM"])
                donary[years["YEAR"]]["FTAMAX"] = max(donary[years["YEAR"]]["FTAMAX"], years["FTA"])
                donary[years["YEAR"]]["FT_PCTMAX"] = max(donary[years["YEAR"]]["FT_PCTMAX"], years["FT_PCT"])
                donary[years["YEAR"]]["OREBMAX"] = max(donary[years["YEAR"]]["OREBMAX"], years["OREB"])
                donary[years["YEAR"]]["DREBMAX"] = max(donary[years["YEAR"]]["DREBMAX"], years["DREB"])
                donary[years["YEAR"]]["REBMAX"] = max(donary[years["YEAR"]]["REBMAX"], years["REB"])
                donary[years["YEAR"]]["ASTMAX"] = max(donary[years["YEAR"]]["ASTMAX"], years["AST"])
                donary[years["YEAR"]]["PFMAX"] = max(donary[years["YEAR"]]["PFMAX"], years["PF"])
                donary[years["YEAR"]]["STLMAX"] = max(donary[years["YEAR"]]["STLMAX"], years["STL"])
                donary[years["YEAR"]]["TOVMAX"] = max(donary[years["YEAR"]]["TOVMAX"], years["TOV"])
                donary[years["YEAR"]]["BLKMAX"] = max(donary[years["YEAR"]]["BLKMAX"], years["BLK"])
                donary[years["YEAR"]]["PTSMAX"] = max(donary[years["YEAR"]]["PTSMAX"], years["PTS"])
                
                
                ddoanry[years["YEAR"]]["GP"] += years["GP"]
                ddoanry[years["YEAR"]]["FGM"] += years["FGM"]
                ddoanry[years["YEAR"]]["FGA"] += years["FGA"]
                ddoanry[years["YEAR"]]["FG3M"] += years["FG3M"]
                ddoanry[years["YEAR"]]["FG3A"] += years["FG3A"]
                ddoanry[years["YEAR"]]["FTM"] += years["FTM"]
                ddoanry[years["YEAR"]]["FTA"] += years["FTA"]
                ddoanry[years["YEAR"]]["OREB"] += years["OREB"]
                ddoanry[years["YEAR"]]["DREB"] += years["DREB"]
                ddoanry[years["YEAR"]]["REB"] += years["REB"]
                ddoanry[years["YEAR"]]["AST"] += years["AST"]
                ddoanry[years["YEAR"]]["PF"] += years["PF"]
                ddoanry[years["YEAR"]]["STL"] += years["STL"]
                ddoanry[years["YEAR"]]["TOV"] += years["TOV"]
                ddoanry[years["YEAR"]]["BLK"] += years["BLK"]
                ddoanry[years["YEAR"]]["PTS"] += years["PTS"]
                ddoanry[years["YEAR"]]["NOT"] += 1


with open("files/teams_high_low_per_years.json", "w", encoding="utf-8") as o_f:
    json.dump(donary, o_f, indent=4)

with open("files/teams_sum_years.json", "w", encoding="utf-8") as o_f:
    json.dump(ddoanry, o_f, indent=4)