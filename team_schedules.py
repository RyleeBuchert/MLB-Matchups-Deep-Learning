import pandas as pd
import statsapi
import os


# Open player/team search files
player_search = pd.read_csv("data\\player_search.csv", encoding = "ISO-8859-1")
team_search = pd.read_csv("data\\team_search.csv")


# Get schedules for each team between 2015-2021
date_dict = {
    "2015_start": "04/05/2015",
    "2015_end": "10/04/2015",
    "2016_start": "04/03/2016",
    "2016_end": "10/02/2016",
    "2017_start": "04/02/2017",
    "2017_end": "10/01/2017",
    "2018_start": "03/28/2018",
    "2018_end": "09/30/2018",
    "2019_start": "03/27/2019",
    "2019_end": "09/29/2019",
    "2020_start": "07/23/2020",
    "2020_end": "09/27/2020",
    "2021_start":"04/01/2021",
    "2021_end":"10/03/2021"
}


# Get all team schedules for 2015-2021 seasons
for team_id in team_search['statsapi_id']:
    for year in [2015,2016,2017,2018,2019,2020,2021]:
        team_schedule = []
        try:
            schedule = statsapi.schedule(start_date=date_dict[f"{year}_start"], end_date=date_dict[f"{year}_end"], team=team_id)
        except:
            print(team_id)
            continue
        for game in schedule:
            if game['game_type'] == 'R':
                if game['home_id'] == team_id:
                    home = 1
                    opp_id = game['away_id']
                else:
                    home = 0
                    opp_id = game['home_id']

                game_record = [game['game_id'], game['game_date'], game['venue_id'], opp_id, home]
                team_schedule.append(game_record)
            else:
                continue
        
        team_schedule = pd.DataFrame(team_schedule, columns=['game_id','game_date','venue_id','opponent_id','home'])
        file_code = team_search.query(f"statsapi_id == {team_id}")['file_code'].values[0]
        file_path = f'data\\schedules\\{file_code}_{team_id}_{year}.csv'
        if os.path.exists(file_path):
            continue
        else:
            team_schedule.to_csv(file_path)


if __name__ == "__main__":

    print()