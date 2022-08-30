import pandas as pd
import os


# Load data files
wOBA_constants = pd.read_csv("data\\wOBA_constants.csv", index_col=0)
league_averages = pd.read_csv("data\\league_averages.csv", index_col=0)


# Impute gamelogs with league averages
for player in ['batters', 'pitchers']:

    file_count = 0
    for file in os.scandir(f"data\\gamelogs\\{player}"):
        file_count += 1

    count = 0
    for file in os.scandir(f'data\\gamelogs\\{player}'):
        print(f'{player}', str(round((count/file_count*100), 2)) + '%')
        count += 1

        gamelog = pd.read_csv(file, index_col=0)
        gamelog = gamelog.loc[gamelog['date'] > '2015-01-01']
        gamelog['imputed'] = 0

        for index, row in gamelog.iterrows():
            year = int(row['game_code'].split("-")[1])
            year_avg = league_averages.loc[year]

            if row['r_PA'] < 20:
                gamelog.loc[index, 'imputed']  = 1
                gamelog.loc[index, 'r_PA']     = round((year_avg['PA'] / 9) * 18)
                gamelog.loc[index, 'r_1B_PA']  = round(year_avg['1B'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_2B_PA']  = round(year_avg['2B'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_3B_PA']  = round(year_avg['3B'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_HR_PA']  = round(year_avg['HR'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_BB_PA']  = round(year_avg['BB'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_IBB_PA'] = round(year_avg['IBB'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_HBP_PA'] = round(year_avg['HBP'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_GDP_PA'] = round(year_avg['GDP'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_K_PA']   = round(year_avg['SO'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_SF_PA']  = round(year_avg['SF'] / year_avg['PA'], 3)
                if player == 'batters':
                    gamelog.loc[index, 'r_SH_PA']  = round(year_avg['SH'] / year_avg['PA'], 3)
                gamelog.loc[index, 'r_avg_pf'] = 100
                
                wOBA_row = wOBA_constants.loc[year]
                wOBA_num = (wOBA_row['wBB']*year_avg['BB'])+(wOBA_row['wHBP']*year_avg['HBP'])+(wOBA_row['w1B']*year_avg['1B'])+(wOBA_row['w2B']*year_avg['2B'])+(wOBA_row['w3B']*year_avg['3B'])+(wOBA_row['wHR']*year_avg['HR'])
                wOBA_denom = year_avg['AB'] + (year_avg['BB'] - year_avg['IBB']) + year_avg['SF'] + year_avg['HBP']
                gamelog.loc[index,'r_wOBA'] = round(wOBA_num / wOBA_denom, 3)

            if row['h_PA'] < 40:
                gamelog.loc[index, 'imputed']  = 1
                gamelog.loc[index, 'h_PA']     = round((year_avg['PA'] / 9) * 162)
                gamelog.loc[index, 'h_1B_PA']  = round(year_avg['1B'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_2B_PA']  = round(year_avg['2B'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_3B_PA']  = round(year_avg['3B'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_HR_PA']  = round(year_avg['HR'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_BB_PA']  = round(year_avg['BB'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_IBB_PA'] = round(year_avg['IBB'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_HBP_PA'] = round(year_avg['HBP'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_GDP_PA'] = round(year_avg['GDP'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_K_PA']   = round(year_avg['SO'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_SF_PA']  = round(year_avg['SF'] / year_avg['PA'], 3)
                if player == 'batters':
                    gamelog.loc[index, 'h_SH_PA']  = round(year_avg['SH'] / year_avg['PA'], 3)
                gamelog.loc[index, 'h_avg_pf'] = 100
                
                wOBA_row = wOBA_constants.loc[year]
                wOBA_num = (wOBA_row['wBB']*year_avg['BB'])+(wOBA_row['wHBP']*year_avg['HBP'])+(wOBA_row['w1B']*year_avg['1B'])+(wOBA_row['w2B']*year_avg['2B'])+(wOBA_row['w3B']*year_avg['3B'])+(wOBA_row['wHR']*year_avg['HR'])
                wOBA_denom = year_avg['AB'] + (year_avg['BB'] - year_avg['IBB']) + year_avg['SF'] + year_avg['HBP']
                gamelog.loc[index, 'h_wOBA'] = round(wOBA_num / wOBA_denom, 3)

        gamelog.to_csv(f"data\\gamelogs\\{player}2\\{file.name}")
