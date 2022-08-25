import pandas as pd
import string
import os


# Open player/team search files
player_search = pd.read_csv("data\\player_search.csv", encoding = "ISO-8859-1")
team_search = pd.read_csv("data\\team_search.csv")


# Get all plate appearances for 2015-2021 seasons
for year in [2015,2016,2017,2018,2019,2020,2021]:
    matchup_data = []
    for file in os.scandir(f"data\\retrosheet\\{year}"):
        f = open(file.path)
        line = f.readline().strip()

        while line != "":
            parts = line.split(",")

            # Get starting pitchers
            if parts[0] == "id":
                while parts[0] != "play":
                    line = f.readline().strip()
                    parts = line.split(",")
                    if parts[0] == "start" and parts[-1] == "1":
                        if parts[3] == "0":
                            away_pitcher = parts[1]
                        else:
                            home_pitcher = parts[1]

            # Get matchups data
            if parts[0] == "play":
                # Get home/away and player ID's
                batter = int(player_search.query(f"key_retro == '{parts[3]}'")['key_mlbam'])
                batter_home = 0
                pitcher = int(player_search.query(f"key_retro == '{home_pitcher}'")['key_mlbam'])
                pitcher_home = 1

                if parts[2] == "1":
                    batter_home = 1
                    pitcher = int(player_search.query(f"key_retro == '{away_pitcher}'")['key_mlbam'])
                    pitcher_home = 0

                outcome = ""

                # Handle balks, intentional walks, HBP, K, and BB
                if parts[-1][:2] in {"BK", "IW", "HP"}:
                    outcome = "p_" + parts[-1][:2]
                elif parts[-1][0] in {"K", "I", "W"}:
                    outcome = "p_" + parts[-1][0]

                # Get pitch outcome if resulted in contact
                pitches = parts[5]
                if len(pitches) > 0 and pitches[-1] == "X":
                    play_parts = parts[6].split("/")
                    main_play = play_parts[0]
                    play = main_play.split(".")[0]

                    if play[0] == "H":
                        play = "HR"
                    elif play[0] in string.digits:
                        play = play[0]
                    elif play[0] in {"S", "D", "T"}:
                        play = play[:2]
                        # Try to get first ball handler
                        if len(play) < 2:
                            try:
                                handlers = play_parts[1]
                                if handlers in string.digits:
                                    play = play[0] + handlers[0]
                            except IndexError:
                                play = play[0] + "X"
                    elif play[:2] == "FC":
                        # Some data doesn't list fielder
                        if len(play) > 2:
                            play = play[2]
                        else:
                            # Handle sacrifice bunts
                            if play_parts[1] == 'SH':
                                play = play_parts[2][2]
                            else:
                                play = play_parts[1][1]
                    
                    outcome = "h_" + play
                    
                # Ignore catcher interference and ambiguous singles.
                if outcome not in {"h_C", "h_S"} and outcome != "":
                    matchup_data.append([parts[1], batter, batter_home, pitcher, pitcher_home, outcome])

            # Handle pitcher changes.
            if parts[0] == "sub":
                if parts[-1] == "1":
                    if parts[3] == "0":
                        away_pitcher = parts[1]
                    else:
                        home_pitcher = parts[1]
            
            line = f.readline().strip()
                        
        f.close()      

    matchup_data = pd.DataFrame(matchup_data, columns=['inning','batter_id','batter_home','pitcher_id','pitcher_home','outcome'])
    matchup_data.to_csv(f'data\\matchups\\{year}_matchups.csv')


if __name__ == "__main__":

    print()