from operator import index
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os


# Function to retrieve a batter's gamelog from 2014-2021
def get_batter_gamelogs(player_id):
    batting_log_data = []
    for year in [2014,2015,2016,2017,2018,2019,2020,2021]:
        url = f"https://www.baseball-reference.com/players/gl.fcgi?id={player_id}&t=b&year={year}"
        soup = BeautifulSoup(requests.get(url).content, 'html5lib')

        batting_log = soup.find_all("table", {"id":"batting_gamelogs"})
        if batting_log:
            batting_log = batting_log[0].contents[7].contents

            batting_log_year = []
            for game in batting_log:
                if isinstance(game, str):
                    continue
                elif 'class' in game.attrs:
                    if game.attrs['class'][0] == 'thead':
                        continue
                    elif game.attrs['class'][0] == 'partial_table':
                        continue

                game_record = []
                for i in [3,4,5,6,-1]:
                    try:
                        game_record.append(game.contents[i].contents[0])
                    except:
                        game_record.append('NA')

                for i in [9,10,11,12,13,14,15,16,17,18,19,20,21,22,24]:
                    try:
                        game_record.append(int(game.contents[i].contents[0]))
                    except IndexError:
                        game_record.append(0)

                split_date = game_record[0].attrs['href'].split(".")[0][-9:-1]
                game_record[0] = "{}-{}-{}".format(split_date[:4],split_date[4:6],split_date[6:8])

                game_record[1] = game_record[1].contents[0]
                game_record[3] = game_record[3].contents[0]

                if game_record[2] == '@':
                    game_record[2] = 'A'
                    game_record.append("{}-{}".format(game_record[3], game_record[0]))
                else:
                    game_record[2] = 'H'
                    game_record.append("{}-{}".format(game_record[1], game_record[0]))

                batting_log_year.append(game_record)
            
            cols = ['date','team','side','opp','pos','PA','AB','R','H','2B','3B','HR','RBI','BB','IBB','K','HBP','SH','SF','GDP','game_code']
            batting_log_data.append(pd.DataFrame(batting_log_year, columns=cols))

    batting_log_data = pd.concat(batting_log_data)
    batting_log_data = batting_log_data[['game_code','date','team','side','opp','pos','PA','AB','R','H','2B','3B','HR','RBI','BB','IBB','K','HBP','SH','SF','GDP']]
    return(batting_log_data)


# Function to retrieve a pitcher's gamelog from 2014-2021
def get_pitcher_gamelogs(player_id):
    pitching_log_data = []
    for year in [2014,2015,2016,2017,2018,2019,2020,2021]:
        url = f"https://www.baseball-reference.com/players/gl.fcgi?id={player_id}&t=p&year={year}"
        soup = BeautifulSoup(requests.get(url).content, 'html5lib')

        pitching_log = soup.find_all("table", {"id":"pitching_gamelogs"})
        if pitching_log:
            pitching_log = pitching_log[0].contents[7].contents

            pitching_log_year = []
            for game in pitching_log:
                if isinstance(game, str):
                    continue
                elif 'class' in game.attrs:
                    if game.attrs['class'][0] == 'thead':
                        continue
                    elif game.attrs['class'][0] == 'partial_table':
                        continue

                game_record = []
                for i in [3,4,5,6,11]:
                    try:
                        game_record.append(game.contents[i].contents[0])
                    except:
                        game_record.append('NA')

                for i in [10,14,12,37,38,39,40,41,42,15,16,17,18,21,26,27,28,29]:
                    try:
                        game_record.append(int(game.contents[i].contents[0]))
                    except IndexError:
                        game_record.append(0)

                split_date = game_record[0].attrs['href'].split(".")[0][-9:-1]
                game_record[0] = "{}-{}-{}".format(split_date[:4],split_date[4:6],split_date[6:8])
                    
                game_record[1] = game_record[1].contents[0]
                game_record[3] = game_record[3].contents[0]

                if game_record[2] == '@':
                    game_record[2] = 'A'
                    game_record.append("{}-{}".format(game_record[3], game_record[0]))
                else:
                    game_record[2] = 'H'
                    game_record.append("{}-{}".format(game_record[1], game_record[0]))

                pitching_log_year.append(game_record)

            cols = ['date','team','side','opp','IP','days_rest','ER','H','AB','2B','3B','IBB',
                    'GDP','SF','BB','K','HR','HBP','PA','GB','FB','LD','PU','game_code']
            pitching_log_data.append(pd.DataFrame(pitching_log_year, columns=cols))

    pitching_log_data = pd.concat(pitching_log_data)
    pitching_log_data = pitching_log_data[['game_code','date','team','side','opp','PA','AB','IP','ER','H','2B','3B','HR',
                                           'BB','IBB','K','HBP','SF','GDP','GB','FB','LD','PU','days_rest']]
    return(pitching_log_data)


if __name__ == "__main__":

    # Open matchups file and get unique lists of batters/pitchers
    player_search = pd.read_csv("data\\player_search.csv", encoding = "ISO-8859-1")
    matchups = pd.concat([pd.read_csv(file) for file in os.scandir(f"data\\matchups")])

    batter_list = list(matchups['batter_id'].unique())
    batter_list.sort()

    pitcher_list = list(matchups['pitcher_id'].unique())
    pitcher_list.sort()

    # Create gamelogs for each batter in list
    count = 0
    for batter in batter_list:
        print('Batters:', str(round((count/len(batter_list)*100), 2)) + '%')
        count += 1
        try:
            bbref_id = player_search.query(f"key_mlbam == {batter}")['key_bbref'].values[0]
            batter_gamelog = get_batter_gamelogs(bbref_id)
            batter_gamelog.to_csv(f'data\\gamelogs\\batters\\{batter}.csv')
        except:
            print(f"Error --- {bbref_id}")
            continue

    # Create gamelogs for each pitcher in list
    count = 0
    for pitcher in pitcher_list:
        print('Pitchers', str(round((count/len(pitcher_list)*100), 2)) + '%')
        count += 1
        try:
            bbref_id = player_search.query(f"key_mlbam == {pitcher}")['key_bbref'].values[0]
            pitcher_gamelog = get_pitcher_gamelogs(bbref_id)
            pitcher_gamelog.to_csv(f'data\\gamelogs\\pitchers\\{pitcher}.csv')
        except:
            print(f"Error --- {bbref_id}")
            continue

    # Add park factors to gamelogs
    park_factors = pd.read_csv("data\\park_factors.csv", index_col=0)
    
    for file in os.scandir('data\\gamelogs\\batters'):
        batter = int(file.name.split(".")[0])
        gamelog = pd.read_csv(file, index_col=0)
        gamelog['w_park_factor'] = gamelog.apply(lambda row: row['PA'] * park_factors.loc[row['game_code'].split("-")[0], row['game_code'].split("-")[1]], axis=1)
        gamelog.to_csv(f'data\\gamelogs\\batters\\{batter}.csv')

    for file in os.scandir('data\\gamelogs\\pitchers'):
        pitcher = int(file.name.split(".")[0])
        gamelog = pd.read_csv(file, index_col=0)
        gamelog['w_park_factor'] = gamelog.apply(lambda row: row['PA'] * park_factors.loc[row['game_code'].split("-")[0], row['game_code'].split("-")[1]], axis=1)
        gamelog.to_csv(f'data\\gamelogs\\pitchers\\{pitcher}.csv')
