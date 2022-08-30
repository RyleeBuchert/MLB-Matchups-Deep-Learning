import pandas as pd
import json


# Load requisite files
wOBA_constants = pd.read_csv("data\\wOBA_constants.csv", index_col=0)
matchups = pd.read_csv("data\\matchups\\all_matchups.csv", index_col=0)

batter_list = list(matchups['batter_id'].unique())
batter_list.sort()

pitcher_list = list(matchups['pitcher_id'].unique())
pitcher_list.sort()


# Batter platoon stats
count = 0
batter_platoons = {}
for batter in batter_list:
    print(f"Batters: {round((count/len(batter_list))*100, 2)}%")
    count += 1
    batter_platoons[int(batter)] = {}
    for side in ['R', 'L']:
        batter_matchups = matchups.loc[(matchups['batter_id'] == batter) & (matchups['pitcher_hand'] == side)]

        num_pa = len(batter_matchups)
        outcomes = batter_matchups.groupby(['outcome']).size()
        indexes = outcomes.index.tolist()

        singles = 0
        for event in ['h_S1','h_S2','h_S3','h_S4','h_S5','h_S6','h_S7','h_S8','h_S9']:
            if event in indexes:
                singles += int(outcomes[event])

        doubles = 0
        for event in ['h_D1','h_D2','h_D3','h_D4','h_D5','h_D6','h_D7','h_D8','h_D9']:
            if event in indexes:
                doubles += int(outcomes[event])

        triples = 0
        for event in ['h_T1','h_T2','h_T3','h_T4','h_T5','h_T6','h_T7','h_T8','h_T9']:
            if event in indexes:
                triples += int(outcomes[event])

        home_runs = 0
        if 'h_HR' in indexes:
            home_runs += int(outcomes['h_HR'])

        bb = 0
        if 'p_W' in indexes:
            bb += int(outcomes['p_W'])

        ibb = 0
        if 'IW' in indexes:
            ibb += int(outcomes['IW'])

        hbp = 0
        if 'HP' in indexes:
            hbp += int(outcomes['HP'])

        at_bats = outcomes.sum()-bb-hbp

        wOBA_row = wOBA_constants.loc['Average']
        wOBA_num = (wOBA_row['wBB']*bb)+(wOBA_row['wHBP']*hbp)+(wOBA_row['w1B']*singles)+(wOBA_row['w2B']*doubles)+(wOBA_row['w3B']*triples)+(wOBA_row['wHR']*home_runs)
        wOBA_denom = at_bats + (bb - ibb) + hbp

        if wOBA_denom:
            wOBA = round(wOBA_num/wOBA_denom, 3)
        else:
            wOBA = 0

        batter_platoons[batter][side] = (num_pa, wOBA)


# Pitcher platoon stats
count = 0
pitcher_platoons = {}
for pitcher in pitcher_list:
    print(f"Pitchers: {round((count/len(pitcher_list))*100, 2)}%")
    count += 1
    pitcher_platoons[int(pitcher)] = {}
    for side in ['R', 'L']:
        pitcher_matchups = matchups.loc[(matchups['pitcher_id'] == pitcher) & (matchups['batter_hand'] == side)]

        num_pa = len(pitcher_matchups)
        outcomes = pitcher_matchups.groupby(['outcome']).size()
        indexes = outcomes.index.tolist()

        singles = 0
        for event in ['h_S1','h_S2','h_S3','h_S4','h_S5','h_S6','h_S7','h_S8','h_S9']:
            if event in indexes:
                singles += int(outcomes[event])

        doubles = 0
        for event in ['h_D1','h_D2','h_D3','h_D4','h_D5','h_D6','h_D7','h_D8','h_D9']:
            if event in indexes:
                doubles += int(outcomes[event])

        triples = 0
        for event in ['h_T1','h_T2','h_T3','h_T4','h_T5','h_T6','h_T7','h_T8','h_T9']:
            if event in indexes:
                triples += int(outcomes[event])

        home_runs = 0
        if 'h_HR' in indexes:
            home_runs += int(outcomes['h_HR'])

        bb = 0
        if 'p_W' in indexes:
            bb += int(outcomes['p_W'])

        ibb = 0
        if 'IW' in indexes:
            ibb += int(outcomes['IW'])

        hbp = 0
        if 'HP' in indexes:
            hbp += int(outcomes['HP'])

        at_bats = outcomes.sum()-bb-hbp

        wOBA_row = wOBA_constants.loc['Average']
        wOBA_num = (wOBA_row['wBB']*bb)+(wOBA_row['wHBP']*hbp)+(wOBA_row['w1B']*singles)+(wOBA_row['w2B']*doubles)+(wOBA_row['w3B']*triples)+(wOBA_row['wHR']*home_runs)
        wOBA_denom = at_bats + (bb - ibb) + hbp

        if wOBA_denom:
            wOBA = round(wOBA_num/wOBA_denom, 3)
        else:
            wOBA = 0

        pitcher_platoons[pitcher][side] = (num_pa, wOBA)


# Save platoon dictionaries
batter_platoon_json = json.dumps(batter_platoons)
with open('data\\batter_platoons.json', 'w') as f:
    f.write(batter_platoon_json)

pitcher_platoon_json = json.dumps(pitcher_platoons)
with open('data\\pitcher_platoons.json', 'w') as f:
    f.write(pitcher_platoon_json)
