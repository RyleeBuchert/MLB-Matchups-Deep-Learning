import pandas as pd
import json
import os

from bs4 import BeautifulSoup
import requests


def get_pitcher_hand(player_id):
    url = f"https://baseballsavant.mlb.com/savant-player/{player_id}"
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    try:
        return(soup.find_all("div", {"class":"bio-player-name"})[0].contents[3].contents[2].strip().split(": ")[1].split("/")[1])
    except:
        print(f"Error --- {player_id}")
        return('NA')


def get_batter_hand(player_id):
    url = f"https://baseballsavant.mlb.com/savant-player/{player_id}"
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')
    try: 
        return(soup.find_all("div", {"class":"bio-player-name"})[0].contents[3].contents[2].strip().split(": ")[1].split("/")[0])
    except:
        print(f"Error --- {player_id}")
        return('NA')


if __name__ == "__main__":
    
    matchups = pd.concat([pd.read_csv(file) for file in os.scandir(f"data\\matchups")])

    pitcher_list = list(matchups['pitcher_id'].unique())
    pitcher_list.sort()

    batter_list = list(matchups['batter_id'].unique())
    batter_list.sort()


    count = 0
    pitcher_hands = {}
    for pitcher in pitcher_list:
        pitcher_hands[int(pitcher)] = get_pitcher_hand(pitcher)
        print('Pitchers:', str(round((count/len(pitcher_list)*100), 2)) + '%' + f' --- {pitcher_hands[pitcher]}')
        count += 1

    pitcher_dict_json = json.dumps(pitcher_hands)
    with open('data\\pitcher_hands.json', 'w') as f:
        f.write(pitcher_dict_json)


    count = 0
    batter_hands = {}
    for batter in batter_list:
        batter_hands[int(batter)] = get_batter_hand(batter)
        print('Batters:', str(round((count/len(batter_list)*100), 2)) + '%' + f' --- {batter_hands[batter]}')
        count += 1

    batter_dict_json = json.dumps(batter_hands)
    with open('data\\batter_hands.json', 'w') as f:
        f.write(batter_dict_json)