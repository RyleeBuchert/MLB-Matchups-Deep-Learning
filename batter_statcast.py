import pybaseball as pyb
import pandas as pd
import requests
from bs4 import BeautifulSoup

from pybaseball import statcast_batter
from pybaseball import playerid_lookup


# Function to retrieve batter statcast table
def get_batter_statcast(player_id):

    # Dictionary for pitch names and acronyms
    pitch_lookup = {
        '4-Seam Fastball': 'FF',
        '4-Seamer': 'FF',
        'Fastball': 'FF',
        'Cutter': 'FC',
        'Sinker': 'SI',
        'Slider': 'SL',
        'Splitter': 'FS',
        'Split-Finger': 'FS',
        'Changeup': 'CH',
        'Curveball': 'CU',
        'Knuckle Curve':'CU',
        'Eephus': 'EE',
        'Knuckleball': 'KN',
        'Intentional Ball': 'IB',
        'Pitch Out': 'PO',
        'N/A': 'NA'
    }

    url = f"https://baseballsavant.mlb.com/savant-player/aaron-judge-{player_id}?stats=statcast-r-hitting-mlb"
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    run_values_data = []
    run_values = soup.find_all("table", {"id": "runValues"})[0].contents[3].contents
    for row in run_values:
        if isinstance(row, str):
            continue

        record_data = []
        record_data.append(row.contents[1].contents[0])

        count = 0
        for record in row.find_all("span"):
            if count == 3:
                record_data.append(row.contents[9].contents[0])
            
            if record.contents:
                record_data.append(record.contents[0])
            
            count += 1

        run_values_data.append(record_data)
    
    # Create dataframe
    run_values_data = pd.DataFrame(run_values_data, columns=['year','pitch','rv_100','run_value','count','pct',
                                                             'PA','BA','SLG','wOBA','whiff_pct','k_pct',
                                                             'put_away_pct','xBA','xSLG','xwOBA','hard_hit_pct'])

    # Clean up missing values
    run_values_data = run_values_data.fillna('')
    run_values_data = run_values_data.replace('--', '')

    # Fix data types
    run_values_data['count'] = run_values_data.apply(lambda row: str.replace(row['count'], ',', ''), axis=1).astype(int)
    run_values_data[['year','rv_100','run_value','count','pct','PA','BA','SLG','wOBA',
                     'whiff_pct','k_pct','put_away_pct','xBA','xSLG','xwOBA','hard_hit_pct']] = run_values_data[[
                     'year','rv_100','run_value','count','pct','PA','BA','SLG','wOBA',
                     'whiff_pct','k_pct','put_away_pct','xBA','xSLG','xwOBA','hard_hit_pct']].apply(pd.to_numeric, errors='coerce')
    run_values_data['pitch_code'] = run_values_data.apply(lambda row: pitch_lookup[row['pitch']], axis=1)
    run_values_data = run_values_data[['year','pitch','pitch_code','count','pct','run_value','rv_100','PA',
                                       'BA','SLG','wOBA','xBA','xSLG','xwOBA','whiff_pct','k_pct','put_away_pct','hard_hit_pct']]

    return(run_values_data)


if __name__ == "__main__":

    batter_statcast = get_batter_statcast(592450)
    print()