import pandas as pd
import statsapi
import json
import os


# Function to convert inning to real number
def inning_convert(innings_pitched):
    if innings_pitched[-2:] == '.1':
        ip = int(innings_pitched) + 0.333333
    elif innings_pitched[-2:] == '.2':
        ip = int(innings_pitched) + 0.666667
    else:
        ip = innings_pitched

    return ip


# Open matchups file and get unique batters/pitchers
matchups = pd.concat([pd.read_csv(file) for file in os.scandir(f"data\\matchups")])

batter_list = list(matchups['batter_id'].unique())
batter_list.sort()

pitcher_list = list(matchups['pitcher_id'].unique())
pitcher_list.sort()


# Initialize dictionaries for player games
batter_games = {}
for id in batter_list:
    batter_games[int(id)] = []

pitcher_games = {}
for id in pitcher_list:
    pitcher_games[int(id)] = []


# Get team boxscores for batting/pitching stats
for item in os.scandir('data\\schedules'):
    print(f"{item.name}")
    file = pd.read_csv(item)
    team_id = int(item.name.split("_")[1])
    for game_id in file['game_id'].tolist():
        boxscore = statsapi.boxscore_data(game_id)

        game_date = boxscore['gameId'].split("/")
        game_date = "{}-{}-{}".format(game_date[0], game_date[1], game_date[2])

        if boxscore['teamInfo']['home']['id'] == team_id:
            status = 'home'
        else:
            status = 'away'

        count = 0
        batter_boxscore = []
        for batter in boxscore[f'{status}Batters']:
            if count == 0:
                count += 1
                continue

            batter_id = int(batter['personId'])
            plate_appearances = int(batter['ab'])+int(batter['bb'])
            
            line = [batter_id, plate_appearances, int(batter['ab']), int(batter['h']),
                    (int(batter['h'])-int(batter['doubles'])-int(batter['triples'])-int(batter['hr'])),
                    int(batter['doubles']), int(batter['triples']), int(batter['hr']),
                    int(batter['rbi']), int(batter['r']), int(batter['bb']), int(batter['k'])]
            batter_boxscore.append(line)

            if plate_appearances:
                batter_games[batter_id].append([f"{game_id}_{status[0]}", game_date])
        
        cols = ['batter_id','PA','AB','H','Singles','Doubles','Triples','HR','RBI','R','BB','K']
        batter_boxscore = pd.DataFrame(batter_boxscore, columns=cols)
        batter_boxscore.to_csv(f'data\\boxscores\\{game_id}_{status[0]}.csv')

        count = 0
        pitcher_boxscore = []
        for pitcher in boxscore[f'{status}Pitchers']:
            if count == 0:
                count += 1
                continue

            pitcher_id = int(pitcher['personId'])
            innings_pitched = inning_convert(pitcher['ip'])

            line = [pitcher_id, innings_pitched, pitcher['h'], pitcher['er'], pitcher['bb'],
                    pitcher['k'], pitcher['hr'], pitcher['p'], pitcher['s']]
            pitcher_boxscore.append(line)

            if innings_pitched:
                pitcher_games[pitcher_id].append([f"{game_id}_{status[0]}", game_date])

        cols = ['pitcher_id']
        pitcher_boxscore = pd.DataFrame(pitcher_boxscore, columns=cols)
        pitcher_boxscore.to_csv(f'data\\boxscores\\{game_id}_{status[0]}.csv')
        

# Save player game dictionaries
batter_dict_json = json.dumps(batter_games)
with open('data\\batter_games.json', 'w') as f:
    f.write(batter_dict_json)

pitcher_dict_json = json.dumps(pitcher_games)
with open('data\\pitcher_games.json', 'w') as f:
    f.write(pitcher_dict_json)


if __name__ == "__main__":

    with open('data\\batter_games.json') as f:
        batter_games_dict = json.load(f)

    with open('data\\boxscores\\415973_a.csv') as f:
        test = pd.read_csv(f)