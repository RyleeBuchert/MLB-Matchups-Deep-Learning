import pybaseball as pyb
import pandas as pd
import requests
from bs4 import BeautifulSoup

from pybaseball import statcast_pitcher
from pybaseball import playerid_lookup


# Function to get table of a player's pitches and stats
def get_pitch_arsenal(player_id):
    
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
        'Intentional Ball': 'IB',
        'Pitch Out': 'PO',
        'Eephus': 'EE'
    }

    # Get summary stats for pitch arsenal
    pitcher_data = statcast_pitcher('2015-01-01', '2022-12-31', player_id)
    pitch_summary = pitcher_data[['player_name','pitcher','game_year','pitch_type','pitch_name',
                        'release_speed','effective_speed','release_pos_x','release_pos_z',
                        'release_extension','release_spin_rate','spin_axis','zone']]
    pitch_summary['pitcher'] = pitch_summary['pitcher'].astype(int)
    pitch_summary = pitch_summary.groupby(['game_year', 'pitch_name']).mean().reset_index(inplace=False)
    pitch_summary['pitch_id'] = pitch_summary.apply(lambda row: "-".join([str(row['pitcher'])[:-2], str(row['game_year']), pitch_lookup[row['pitch_name']]]), axis=1)
    pitch_summary = pitch_summary[[list(pitch_summary.columns)[-1]] + list(pitch_summary.columns)[:-1]].drop(['pitcher'], axis=1)
    pitch_summary = pitch_summary.round(3)


    # Scrape html from pitcher's baseball savant page
    url = f"https://baseballsavant.mlb.com/savant-player/{player_id}?stats=statcast-r-pitching-mlb"
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')


    # Create pitch movement dataframe
    pitch_movement_data = []
    pitch_movement = soup.find_all("table", {"id": "pitchMovement"})[0].contents[3].contents
    for row in pitch_movement:
        if isinstance(row, str):
            continue

        pitch_movement_data.append([record.contents[0] for record in row.find_all("span") if record.contents])

    pitch_movement_data = pd.DataFrame(pitch_movement_data, columns=['year','pitch','hand','count','speed',
                                                                'vertical_movement','vertical_movement_vs_avg','vertical_movement_pct_vs_avg',
                                                                'horizontal_movement','horizontal_movement_vs_avg','horizontal_movement_pct_vs_avg'])

    # Add pitch_id from records
    pitch_movement_data['pitch_id'] = pitch_movement_data.apply(lambda row: "-".join([str(player_id), row['year'], pitch_lookup[row['pitch']]]), axis=1)
    pitch_movement_data = pitch_movement_data[[list(pitch_movement_data.columns)[-1]] + list(pitch_movement_data.columns)[:-1]].drop(['year', 'pitch'], axis=1)

    # Fix data types
    pitch_movement_data['count'] = pitch_movement_data.apply(lambda row: str.replace(row['count'], ',', ''), axis=1).astype(int)
    pitch_movement_data[['speed','vertical_movement','vertical_movement_vs_avg','vertical_movement_pct_vs_avg',
                        'horizontal_movement','horizontal_movement_vs_avg','horizontal_movement_pct_vs_avg']] = pitch_movement_data[[
                        'speed','vertical_movement','vertical_movement_vs_avg','vertical_movement_pct_vs_avg',
                        'horizontal_movement','horizontal_movement_vs_avg','horizontal_movement_pct_vs_avg']].apply(pd.to_numeric, errors='coerce')


    # Create run value dataframe
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

    run_values_data = pd.DataFrame(run_values_data, columns=['year','pitch','rv_100','run_value','count','usage',
                                                            'PA','BA','SLG','wOBA','whiff_pct','k_pct','put_away_pct',
                                                            'xBA','xSLG','xwOBA','hard_hit_pct'])

    # Add pitch_id from records
    run_values_data['pitch_id'] = run_values_data.apply(lambda row: "-".join([str(player_id), row['year'], pitch_lookup[row['pitch']]]), axis=1)
    run_values_data = run_values_data[[list(run_values_data.columns)[-1]] + list(run_values_data.columns)[:-1]].drop(['year', 'pitch'], axis=1)

    run_values_data = run_values_data.fillna('')
    run_values_data = run_values_data.replace('--', '')

    # Fix data types
    run_values_data['count'] = run_values_data.apply(lambda row: str.replace(row['count'], ',', ''), axis=1).astype(int)
    run_values_data[['PA','run_value','usage','rv_100','BA','SLG','wOBA','xBA','xSLG','xwOBA',
                        'k_pct','put_away_pct','whiff_pct','hard_hit_pct']] = run_values_data[[
                     'PA','run_value','usage','rv_100','BA','SLG','wOBA','xBA','xSLG','xwOBA',
                        'k_pct','put_away_pct','whiff_pct','hard_hit_pct']].apply(pd.to_numeric, errors='coerce')


    # Create spin axis dataframe
    spin_axis_data = []
    spin_axis = soup.find_all("table", {"id": "spinAxis"})[0].contents[3].contents
    for row in spin_axis:
        if isinstance(row, str):
            continue

        record_data = []
        record_data.append(row.contents[1].contents[0])

        for record in row.find_all("span"):
            if record.contents:
                record_data.append(record.contents[0])

        spin_axis_data.append(record_data)

    spin_axis_data = pd.DataFrame(spin_axis_data, columns=['year','pitch','count','speed','active_spin_pct',
                                                        'total_movement','spin_based','observed','deviation'])

    # Add pitch_id from records
    spin_axis_data['pitch_id'] = spin_axis_data.apply(lambda row: "-".join([str(player_id), row['year'], pitch_lookup[row['pitch']]]), axis=1)
    spin_axis_data = spin_axis_data[[list(spin_axis_data.columns)[-1]] + list(spin_axis_data.columns)[:-1]].drop(['year', 'pitch'], axis=1)

    # Fix data types
    spin_axis_data[['active_spin_pct','deviation','total_movement']] = spin_axis_data[[
                    'active_spin_pct','deviation','total_movement']].apply(pd.to_numeric, errors='coerce')


    # Merge tables together to create pitch arsenal df
    pitch_arsenal = pd.merge(
                pd.merge(
                                # Join pitch_movement and run_values data
                        pd.merge(pitch_movement_data[['pitch_id','hand','count',
                                                    'vertical_movement','vertical_movement_vs_avg','vertical_movement_pct_vs_avg',
                                                    'horizontal_movement','horizontal_movement_vs_avg','horizontal_movement_pct_vs_avg']], 
                                run_values_data[['pitch_id','usage','rv_100','run_value',
                                                'PA','BA','SLG','wOBA','xBA','xSLG','xwOBA',
                                                'k_pct','put_away_pct','whiff_pct','hard_hit_pct']],
                                on='pitch_id'),
                        # And then join with spin_axis data
                        spin_axis_data[['pitch_id','active_spin_pct','total_movement']],
                        on='pitch_id',
                        how='left'),
                    # Finally, join with pitch summary data
                    pitch_summary[['pitch_id','game_year','pitch_name','release_speed','effective_speed',
                                'release_pos_x','release_pos_z','release_extension',
                                'release_spin_rate','spin_axis','zone']],
                    on='pitch_id',
                    how='left')

    # Filter out pitches with less than 3% usage
    pitch_arsenal = pitch_arsenal[pitch_arsenal['usage'] >= 3]

    # Re-order columns
    pitch_arsenal = pitch_arsenal[['pitch_id','game_year','hand','pitch_name','count','usage',
                                    'release_speed','effective_speed','release_pos_x','release_pos_z','release_extension',
                                    'release_spin_rate','spin_axis','active_spin_pct','total_movement',
                                    'vertical_movement','vertical_movement_vs_avg','vertical_movement_pct_vs_avg',
                                    'horizontal_movement','horizontal_movement_vs_avg','horizontal_movement_pct_vs_avg',
                                    'zone','rv_100','run_value','PA','BA','SLG','wOBA','xBA','xSLG','xwOBA',
                                    'k_pct','put_away_pct','whiff_pct','hard_hit_pct']]
    return(pitch_arsenal)


if __name__ == "__main__":

    pitch_arsenal = get_pitch_arsenal(642207)
    print()