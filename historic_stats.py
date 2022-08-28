import pandas as pd
import datetime
import os


# Function to add historic/recent per PA stats to pitcher gamelog
def get_pitcher_past_stats(player_data, type):
    
    if type == 'h':
        delta = 365
    elif type == 'r':
        delta = 21

    past_stats = []
    for index, row in player_data.iterrows():
        if row['date'].split("-")[0] == '2014':
            continue

        end_date = row['date']
        start_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(days=delta)
        start_date = "{}-{}-{}".format(start_date.year, str(start_date.month).zfill(2), str(start_date.day).zfill(2))

        stats = player_data.loc[(player_data['date'] > start_date) & (player_data['date'] < end_date)].sum(numeric_only=True)

        pa         = int(stats['PA']) + 1
        singles_pa = round((stats['H']-stats['2B']-stats['3B']-stats['HR'])/pa, 3)
        doubles_pa = round(stats['2B'] / pa, 3)
        triples_pa = round(stats['3B'] / pa, 3)
        hr_pa      = round(stats['HR'] / pa, 3)
        bb_pa      = round(stats['BB'] / pa, 3)
        ibb_pa     = round(stats['IBB'] / pa, 3)
        hbp_pa     = round(stats['HBP'] / pa, 3)
        gdp_pa     = round(stats['GDP'] / pa, 3)
        k_pa       = round(stats['K'] / pa, 3)
        sf_pa      = round(stats['SF'] / pa, 3)

        # Add wOBA constants from file
        wOBA_num = (stats['BB']) + (stats['HBP']) + (stats['1B']) + (stats['2B']) + (stats['3B']) + (stats['HR'])
        wOBA_denom = stats['AB'] + (stats['BB'] - stats['IBB']) + stats['SF'] + stats['HBP']

        past_stats.append([row['game_code'], pa, singles_pa, doubles_pa, triples_pa, hr_pa, bb_pa, ibb_pa, hbp_pa, gdp_pa, k_pa, sf_pa, (wOBA_num/wOBA_denom)])

    if type == 'h':
        cols = ['game_code', 'h_PA', 'h_1B_PA', 'h_2B_PA', 'h_3B_PA', 'h_HR_PA', 'h_BB_PA', 'h_IBB_PA', 'h_HBP_PA', 'h_GDP_PA', 'h_K_PA', 'h_SF_PA', 'wOBA']
    elif type == 'r':
        cols = ['game_code', 'r_PA', 'r_1B_PA', 'r_2B_PA', 'r_3B_PA', 'r_HR_PA', 'r_BB_PA', 'r_IBB_PA', 'r_HBP_PA', 'r_GDP_PA', 'r_K_PA', 'r_SF_PA', 'wOBA']
    return(pd.DataFrame(past_stats, columns=cols))


# Function to add historic/recent per PA stats to batter gamelog
def get_batter_past_stats(player_data, type):
    
    if type == 'h':
        delta = 365
    elif type == 'r':
        delta = 21

    past_stats = []
    for index, row in player_data.iterrows():
        if row['date'].split("-")[0] == '2014':
            continue

        end_date = row['date']
        start_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') - datetime.timedelta(days=delta)
        start_date = "{}-{}-{}".format(start_date.year, str(start_date.month).zfill(2), str(start_date.day).zfill(2))

        stats = player_data.loc[(player_data['date'] > start_date) & (player_data['date'] < end_date)].sum(numeric_only=True)

        pa         = int(stats['PA']) + 1
        singles_pa = round((stats['H']-stats['2B']-stats['3B']-stats['HR'])/pa, 3)
        doubles_pa = round(stats['2B'] / pa, 3)
        triples_pa = round(stats['3B'] / pa, 3)
        hr_pa      = round(stats['HR'] / pa, 3)
        bb_pa      = round(stats['BB'] / pa, 3)
        ibb_pa     = round(stats['IBB'] / pa, 3)
        hbp_pa     = round(stats['HBP'] / pa, 3)
        gdp_pa     = round(stats['GDP'] / pa, 3)
        k_pa       = round(stats['K'] / pa, 3)
        sf_pa      = round(stats['SF'] / pa, 3)
        sh_pa      = round(stats['SH'] / pa, 3)

        # Add wOBA constants from file
        wOBA_num = (stats['BB']) + (stats['HBP']) + (stats['1B']) + (stats['2B']) + (stats['3B']) + (stats['HR'])
        wOBA_denom = stats['AB'] + (stats['BB'] - stats['IBB']) + stats['SF'] + stats['HBP']

        past_stats.append([row['game_code'], pa, singles_pa, doubles_pa, triples_pa, hr_pa, bb_pa, ibb_pa, hbp_pa, gdp_pa, k_pa, sf_pa, sh_pa, (wOBA_num/wOBA_denom)])

    if type == 'h':
        cols = ['game_code', 'h_PA', 'h_1B_PA', 'h_2B_PA', 'h_3B_PA', 'h_HR_PA', 'h_BB_PA', 'h_IBB_PA', 'h_HBP_PA', 'h_GDP_PA', 'h_K_PA', 'h_SF_PA', 'h_SH_PA', 'wOBA']
    elif type == 'r':
        cols = ['game_code', 'r_PA', 'r_1B_PA', 'r_2B_PA', 'r_3B_PA', 'r_HR_PA', 'r_BB_PA', 'r_IBB_PA', 'r_HBP_PA', 'r_GDP_PA', 'r_K_PA', 'r_SF_PA', 'r_SH_PA', 'wOBA']
    return(pd.DataFrame(past_stats, columns=cols))


if __name__ == "__main__":

    file_count = 0
    for file in os.scandir('data\\gamelogs\\batters'):
        file_count += 1

    count = 0
    for file in os.scandir('data\\gamelogs\\batters'):
        print('Batters', str(round((count/file_count*100), 2)) + '%')
        count += 1

        batter = int(file.name.split(".")[0])
        gamelog = pd.read_csv(file, index_col=0)

        gamelog = gamelog.merge(get_batter_past_stats(gamelog, 'h'), how='left', on='game_code')
        gamelog = gamelog.merge(get_batter_past_stats(gamelog, 'r'), how='left', on='game_code').fillna(0)
        gamelog.to_csv(f'data\\gamelogs\\batters\\{batter}.csv')


    file_count = 0
    for file in os.scandir('data\\gamelogs\\pitchers'):
        file_count += 1

    count = 0
    for file in os.scandir('data\\gamelogs\\pitchers'):
        print('Pitchers', str(round((count/file_count*100), 2)) + '%')
        count += 1

        pitcher = int(file.name.split(".")[0])
        gamelog = pd.read_csv(file, index_col=0)

        gamelog = gamelog.merge(get_pitcher_past_stats(gamelog, 'h'), how='left', on='game_code')
        gamelog = gamelog.merge(get_pitcher_past_stats(gamelog, 'r'), how='left', on='game_code').fillna(0)
        gamelog.to_csv(f'data\\gamelogs\\pitchers\\{pitcher}.csv')
