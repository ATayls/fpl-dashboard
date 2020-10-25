import time
import json

import requests
import pandas as pd

fpl_base_url = r'https://fantasy.premierleague.com/api/'

def _fpl_url_request(url):
    """Retrieve data from url request to fpl api"""
    response = ''
    while response == '':
        try:
            response = requests.get(url)
        except:
            time.sleep(5)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    data = json.loads(response.text)
    return data

def get_league_data(leagueId, page_num=1):
    url = fpl_base_url + f'/leagues-classic/{leagueId}/standings?page_standings={page_num}'
    return _fpl_url_request(url)


def get_fixtures_data():
    url = fpl_base_url + "/fixtures/"
    return _fpl_url_request(url)


def get_entry_picks(entry_id, gameweek):
    url = fpl_base_url + f"/entry/{entry_id}/event/{gameweek}/picks/"
    return _fpl_url_request(url)


def league_dataframe(league_id, manager_limit=None):
    all_results = []
    page_num = 1
    while True:
        league_info = get_league_data(league_id, page_num)
        all_results += league_info['standings']['results']
        page_num += 1
        if not league_info['standings']['has_next']:
            league_df = pd.DataFrame.from_records(all_results)
            break
        elif manager_limit and manager_limit < len(all_results):
            league_df = pd.DataFrame.from_records(all_results).head(manager_limit)
            break

    return league_df, league_info['league']['name']


def scrape_manager_team(entry_id, gw_list):
    entry_data_list = []
    for gw in gw_list:
        # Request data
        entry_picks = get_entry_picks(entry_id, gw)
        # Create dict
        gw_data = entry_picks['entry_history']
        captain = None
        for pick in entry_picks['picks']:
            gw_data[f'P{pick["position"]}'] = pick['element']
            if pick['is_captain']:
                captain = pick['element']
        # Add other to dict
        gw_data['captain'] = captain
        gw_data['active_chip'] = entry_picks['active_chip']
        entry_data_list.append(gw_data)
    output_df = pd.DataFrame.from_records(entry_data_list)
    output_df = output_df.rename(columns={'P12': 'S1',
                                          'P13': 'S2',
                                          'P14': 'S3',
                                          'P15': 'S4',
                                          'event': 'gw'})

    return output_df

def get_played_gameweeks(including_active=False):
    fixtures = get_fixtures_data()
    fixtures_df = pd.DataFrame.from_records(fixtures)
    grby = fixtures_df.groupby(by='event').mean()
    if including_active:
        gw_list = grby[grby['finished'] > 0].index.to_list()
    else:
        gw_list = grby[grby['finished'] == 1].index.to_list()
    return [int(gw) for gw in gw_list]

if __name__ == '__main__':

    fixtures = get_fixtures_data()
    df_league = league_dataframe(261, 100)
    df_entry = scrape_manager_team(164, [1, 2, 3])
    df_entry.to_feather('test')
    print("")