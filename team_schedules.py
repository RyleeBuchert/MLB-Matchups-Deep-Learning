import pandas as pd
import statsapi
import os


# Open player/team search files
player_search = pd.read_csv("data\\player_search.csv", encoding="ISO-8859-1")
team_search = pd.read_csv("data\\team_search.csv")


# Get schedules for each team between 2015-2021
date_dict = {
    "2014_start": "03/22/2014",
    "2014_end":   "09/28/2014",
    "2015_start": "04/05/2015",
    "2015_end":   "10/04/2015",
    "2016_start": "04/03/2016",
    "2016_end":   "10/02/2016",
    "2017_start": "04/02/2017",
    "2017_end":   "10/01/2017",
    "2018_start": "03/28/2018",
    "2018_end":   "09/30/2018",
    "2019_start": "03/27/2019",
    "2019_end":   "09/29/2019",
    "2020_start": "07/23/2020",
    "2020_end":   "09/27/2020",
    "2021_start": "04/01/2021",
    "2021_end":   "10/03/2021"
}


# Get all team schedules for 2015-2021 seasons
for team_id in team_search['statsapi_id']:
    team_schedule = []
    file_code = team_search.query(f"statsapi_id == {team_id}")['file_code'].values[0]
    for year in [2014,2015,2016,2017,2018,2019,2020,2021]:
        season = []
        try:
            schedule = statsapi.schedule(start_date=date_dict[f"{year}_start"], end_date=date_dict[f"{year}_end"], team=team_id)
        except:
            print(team_id)
            continue
        for game in schedule:
            if game['game_type'] == 'R':
                date = game['game_date']
                
                if game['home_id'] == team_id:
                    home = 1
                    opp_id = game['away_id']
                    game_code = "{}-{}".format(file_code, date)
                else:
                    home = 0
                    opp_id = game['home_id']
                    game_code = "{}-{}".format(team_search.query(f"statsapi_id == {opp_id}")['file_code'].values[0], date)

                game_record = [game['game_id'], game_code, date, game['venue_id'], opp_id, home]
                season.append(game_record)
            else:
                continue

        team_schedule.append(pd.DataFrame(season, columns=['game_id','game_code','date','venue_id','opp_id','home']))

    team_schedule = pd.concat(team_schedule)
    team_schedule.to_csv(f'data\\schedules\\{file_code}_{team_id}.csv')
