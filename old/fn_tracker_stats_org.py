#!/usr/bin/python

import os
import sys
import time
import json
import csv
import requests
import configparser
import argparse
import logging


logging.basicConfig()
LOGGER = logging.getLogger('fortnite2influx')
LOGGER.setLevel(logging.INFO)

parser = argparse.ArgumentParser(
    description="read Stats from the Fortnite API and export as Json"
)

parser.add_argument("-d", "--debug", action='store_true')
parser.add_argument("-c", "--config",
                    default=os.path.dirname(os.path.abspath(__file__)) + '/fortnite2influx.conf')

args = parser.parse_args()

if args.debug:
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.debug("DEBUG Mode is ON")

if not args.config:
    args.config = os.path.dirname(os.path.abspath(__file__)) + '/fortnite2influx.conf'

LOGGER.debug("Config file path: %s", args.config)


config = dict()
config_f = configparser.ConfigParser()

try:
    config_f.read_file(open(args.config))
    config['fortniteapi_url'] = config_f.get('fortniteapi', 'url')
    config['fortniteapi_API_TOKEN'] = config_f.get('fortniteapi', 'token')
    config['fortnitetracker_url'] = config_f.get('fortnitetracker', 'url')
    config['fortnitetracker_API_TOKEN'] = config_f.get('fortnitetracker', 'token')
    config['season'] = config_f.get('general', 'season')
    season = config['season']
except configparser.ParsingError:
    LOGGER.error("Unable to parse config from file %s!", args.config)
    sys.exit(1)


data_api = {}

def parse_data(data):
    try:
        data_api['name'] = data['epicUserHandle']
        data_api['accountId'] = data['accountId']
        #data_api['country'] = data['country']
        data_api['avatar'] = data['avatar']
        data_api['platformId'] = data['platformId']
        data_api['platformName'] = data['platformName']
        data_api['platformNameLong'] = data['platformNameLong']
        data_api['season'] = int(season)

        data_api['Lifetime_Top5']  = int(data['lifeTimeStats'][0]['value'])
        data_api['Lifetime_Top3']  = int(data['lifeTimeStats'][1]['value'])
        data_api['Lifetime_Top6']  = int(data['lifeTimeStats'][2]['value'])
        data_api['Lifetime_Top10'] = int(data['lifeTimeStats'][3]['value'])
        data_api['Lifetime_Top12'] = int(data['lifeTimeStats'][4]['value'])
        data_api['Lifetime_Top25'] = int(data['lifeTimeStats'][5]['value'])
        
        score_tmp = data['lifeTimeStats'][6]['value']
        score_float = float(score_tmp.replace(',', '.'))

        data_api['Lifetime_Score'] = score_float
        data_api['Lifetime_Matches Played'] = int(data['lifeTimeStats'][7]['value'])
        data_api['Lifetime_Wins'] = int(data['lifeTimeStats'][8]['value'])
        
        win_tmp = data['lifeTimeStats'][9]['value']
        win_percent = float(win_tmp.replace('%', ''))

        data_api['Lifetime_Wins_percent'] = win_percent
        data_api['Lifetime_Kills'] = int(data['lifeTimeStats'][10]['value'])
        data_api['Lifetime_kd'] = float(data['lifeTimeStats'][11]['value'])
        data_api['Lifetime_kill_per_min'] = float(data['lifeTimeStats'][11]['value'])

        data_api['Lifetime_squad_placetop1'] = int(data['stats']['p9']['top1']['value'])
        data_api['Lifetime_squad_placetop3'] = int(data['stats']['p9']['top3']['value'])
        data_api['Lifetime_squad_placetop5'] = int(data['stats']['p9']['top5']['value'])
        data_api['Lifetime_squad_placetop6'] = int(data['stats']['p9']['top6']['value'])
        data_api['Lifetime_squad_placetop10'] = int(data['stats']['p9']['top10']['value'])
        data_api['Lifetime_squad_placetop12'] = int(data['stats']['p9']['top12']['value'])
        data_api['Lifetime_squad_placetop25'] = int(data['stats']['p9']['top25']['value'])
        data_api['Lifetime_squad_kd'] = float(data['stats']['p9']['kd']['value'])
        data_api['Lifetime_squad_winrate'] = float(data['stats']['p9']['winRatio']['value'])
        data_api['Lifetime_squad_kills'] = int(data['stats']['p9']['kills']['value'])
        data_api['Lifetime_squad_matchesplayed'] = int(data['stats']['p9']['matches']['value'])
        data_api['Lifetime_squad_minutesplayed'] = int(data['stats']['p9']['minutesPlayed']['value'])
        data_api['Lifetime_squad_score'] = float(data['stats']['p9']['score']['value'])
        data_api['Lifetime_squad_kpm'] = float(data['stats']['p9']['kpm']['value'])
        data_api['Lifetime_squad_kpg'] = float(data['stats']['p9']['kpg']['value'])
        data_api['Lifetime_squad_scorePerMatch'] = float(data['stats']['p9']['scorePerMatch']['value'])
        data_api['Lifetime_squad_scorePerMin'] = float(data['stats']['p9']['scorePerMin']['value'])
        
        data_api['Lifetime_duo_placetop1'] = int(data['stats']['p10']['top1']['value'])
        data_api['Lifetime_duo_placetop3'] = int(data['stats']['p10']['top3']['value'])
        data_api['Lifetime_duo_placetop5'] = int(data['stats']['p10']['top5']['value'])
        data_api['Lifetime_duo_placetop6'] = int(data['stats']['p10']['top6']['value'])
        data_api['Lifetime_duo_placetop10'] = int(data['stats']['p10']['top10']['value'])
        data_api['Lifetime_duo_placetop12'] = int(data['stats']['p10']['top12']['value'])
        data_api['Lifetime_duo_placetop25'] = int(data['stats']['p10']['top25']['value'])
        data_api['Lifetime_duo_kd'] = float(data['stats']['p10']['kd']['value'])
        data_api['Lifetime_duo_winrate'] = float(data['stats']['p10']['winRatio']['value'])
        data_api['Lifetime_duo_kills'] = int(data['stats']['p10']['kills']['value'])
        data_api['Lifetime_duo_matchesplayed'] = int(data['stats']['p10']['matches']['value'])
        data_api['Lifetime_duo_minutesplayed'] = int(data['stats']['p10']['minutesPlayed']['value'])
        data_api['Lifetime_duo_score'] = float(data['stats']['p10']['score']['value'])
        data_api['Lifetime_duo_kpm'] = float(data['stats']['p10']['kpm']['value'])
        data_api['Lifetime_duo_kpg'] = float(data['stats']['p10']['kpg']['value'])
        data_api['Lifetime_duo_scorePerMatch'] = float(data['stats']['p10']['scorePerMatch']['value'])
        data_api['Lifetime_duo_scorePerMin'] = float(data['stats']['p10']['scorePerMin']['value'])

        data_api['Lifetime_solo_placetop1'] = int(data['stats']['p2']['top1']['value'])
        data_api['Lifetime_solo_placetop3'] = int(data['stats']['p2']['top3']['value'])
        data_api['Lifetime_solo_placetop5'] = int(data['stats']['p2']['top5']['value'])
        data_api['Lifetime_solo_placetop6'] = int(data['stats']['p2']['top6']['value'])
        data_api['Lifetime_solo_placetop10'] = int(data['stats']['p2']['top10']['value'])
        data_api['Lifetime_solo_placetop12'] = int(data['stats']['p2']['top12']['value'])
        data_api['Lifetime_solo_placetop25'] = int(data['stats']['p2']['top25']['value'])
        data_api['Lifetime_solo_kd'] = float(data['stats']['p2']['kd']['value'])
        data_api['Lifetime_solo_winrate'] = float(data['stats']['p2']['winRatio']['value'])
        data_api['Lifetime_solo_kills'] = int(data['stats']['p2']['kills']['value'])
        data_api['Lifetime_solo_matchesplayed'] = int(data['stats']['p2']['matches']['value'])
        data_api['Lifetime_solo_minutesplayed'] = int(data['stats']['p2']['minutesPlayed']['value'])
        data_api['Lifetime_solo_score'] = float(data['stats']['p2']['score']['value'])
        data_api['Lifetime_solo_kpm'] = float(data['stats']['p2']['kpm']['value'])
        data_api['Lifetime_solo_kpg'] = float(data['stats']['p2']['kpg']['value'])
        data_api['Lifetime_solo_scorePerMatch'] = float(data['stats']['p2']['scorePerMatch']['value'])
        data_api['Lifetime_solo_scorePerMin'] = float(data['stats']['p2']['scorePerMin']['value'])

        data_api["season_" + str(season) + "_squad_placetop1"] = int(data['stats']['curr_p9']['top1']['value'])
        data_api["season_" + str(season) + "_squad_placetop3"] = int(data['stats']['curr_p9']['top3']['value'])
        data_api["season_" + str(season) + "_squad_placetop5"] = int(data['stats']['curr_p9']['top5']['value'])
        data_api["season_" + str(season) + "_squad_placetop6"] = int(data['stats']['curr_p9']['top6']['value'])
        data_api["season_" + str(season) + "_squad_placetop10"] = int(data['stats']['curr_p9']['top10']['value'])
        data_api["season_" + str(season) + "_squad_placetop12"] = int(data['stats']['curr_p9']['top12']['value'])
        data_api["season_" + str(season) + "_squad_placetop25"] = int(data['stats']['curr_p9']['top25']['value'])
        data_api["season_" + str(season) + "_squad_kd"] = float(data['stats']['curr_p9']['kd']['value'])
        data_api["season_" + str(season) + "_squad_winrate"] = float(data['stats']['curr_p9']['winRatio']['value'])
        data_api["season_" + str(season) + "_squad_kills"] = int(data['stats']['curr_p9']['kills']['value'])
        data_api["season_" + str(season) + "_squad_matchesplayed"] = int(data['stats']['curr_p9']['matches']['value'])
        data_api["season_" + str(season) + "_squad_minutesplayed"] = int(data['stats']['curr_p9']['minutesPlayed']['value'])
        data_api["season_" + str(season) + "_squad_score"] = float(data['stats']['curr_p9']['score']['value'])
        data_api["season_" + str(season) + "_squad_kpm"] = float(data['stats']['curr_p9']['kpm']['value'])
        data_api["season_" + str(season) + "_squad_kpg"] = float(data['stats']['curr_p9']['kpg']['value'])
        data_api["season_" + str(season) + "_squad_scorePerMatch"] = float(data['stats']['curr_p9']['scorePerMatch']['value'])
        data_api["season_" + str(season) + "_squad_scorePerMin"] = float(data['stats']['curr_p9']['scorePerMin']['value'])

        data_api["season_" + str(season) + "_duo_placetop1"] = int(data['stats']['curr_p10']['top1']['value'])
        data_api["season_" + str(season) + "_duo_placetop3"] = int(data['stats']['curr_p10']['top3']['value'])
        data_api["season_" + str(season) + "_duo_placetop5"] = int(data['stats']['curr_p10']['top5']['value'])
        data_api["season_" + str(season) + "_duo_placetop6"] = int(data['stats']['curr_p10']['top6']['value'])
        data_api["season_" + str(season) + "_duo_placetop10"] = int(data['stats']['curr_p10']['top10']['value'])
        data_api["season_" + str(season) + "_duo_placetop12"] = int(data['stats']['curr_p10']['top12']['value'])
        data_api["season_" + str(season) + "_duo_placetop25"] = int(data['stats']['curr_p10']['top25']['value'])
        data_api["season_" + str(season) + "_duo_kd"] = float(data['stats']['curr_p10']['kd']['value'])
        data_api["season_" + str(season) + "_duo_winrate"] = float(data['stats']['curr_p10']['winRatio']['value'])
        data_api["season_" + str(season) + "_duo_kills"] = int(data['stats']['curr_p10']['kills']['value'])
        data_api["season_" + str(season) + "_duo_matchesplayed"] = int(data['stats']['curr_p10']['matches']['value'])
        data_api["season_" + str(season) + "_duo_minutesplayed"] = int(data['stats']['curr_p10']['minutesPlayed']['value'])
        data_api["season_" + str(season) + "_duo_score"] = float(data['stats']['curr_p10']['score']['value'])
        data_api["season_" + str(season) + "_duo_kpm"] = float(data['stats']['curr_p10']['kpm']['value'])
        data_api["season_" + str(season) + "_duo_kpg"] = float(data['stats']['curr_p10']['kpg']['value'])
        data_api["season_" + str(season) + "_duo_scorePerMatch"] = float(data['stats']['curr_p10']['scorePerMatch']['value'])
        data_api["season_" + str(season) + "_duo_scorePerMin"] = float(data['stats']['curr_p10']['scorePerMin']['value'])

        data_api["season_" + str(season) + "_solo_placetop1"] = int(data['stats']['curr_p2']['top1']['value'])
        data_api["season_" + str(season) + "_solo_placetop3"] = int(data['stats']['curr_p2']['top3']['value'])
        data_api["season_" + str(season) + "_solo_placetop5"] = int(data['stats']['curr_p2']['top5']['value'])
        data_api["season_" + str(season) + "_solo_placetop6"] = int(data['stats']['curr_p2']['top6']['value'])
        data_api["season_" + str(season) + "_solo_placetop10"] = int(data['stats']['curr_p2']['top10']['value'])
        data_api["season_" + str(season) + "_solo_placetop12"] = int(data['stats']['curr_p2']['top12']['value'])
        data_api["season_" + str(season) + "_solo_placetop25"] = int(data['stats']['curr_p2']['top25']['value'])
        data_api["season_" + str(season) + "_solo_kd"] = float(data['stats']['curr_p2']['kd']['value'])
        data_api["season_" + str(season) + "_solo_winrate"] = float(data['stats']['curr_p2']['winRatio']['value'])
        data_api["season_" + str(season) + "_solo_kills"] = int(data['stats']['curr_p2']['kills']['value'])
        data_api["season_" + str(season) + "_solo_matchesplayed"] = int(data['stats']['curr_p2']['matches']['value'])
        data_api["season_" + str(season) + "_solo_minutesplayed"] = int(data['stats']['curr_p2']['minutesPlayed']['value'])
        data_api["season_" + str(season) + "_solo_score"] = float(data['stats']['curr_p2']['score']['value'])
        data_api["season_" + str(season) + "_solo_kpm"] = float(data['stats']['curr_p2']['kpm']['value'])
        data_api["season_" + str(season) + "_solo_kpg"] = float(data['stats']['curr_p2']['kpg']['value'])
        data_api["season_" + str(season) + "_solo_scorePerMatch"] = float(data['stats']['curr_p2']['scorePerMatch']['value'])
        data_api["season_" + str(season) + "_solo_scorePerMin"] = float(data['stats']['curr_p2']['scorePerMin']['value'])
    except KeyError:
        pass

    return data_api

# def parse_data_io(data):
#     try:
#         data_api['account_level'] = data['account']['level']
#         data_api['account_progress_pct'] = data['account']['progress_pct']
#     except KeyError:
#         pass    
#     return data_api


data_api_list = []
csv_file = os.path.dirname(os.path.abspath(__file__)) + '/players.csv'

with open(csv_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
       
        fortnitetracker_url_per_player = config['fortnitetracker_url'] + "/" + str(row['plattform']) + "/" + str(row['player_name']                )      

        response = requests.get(fortnitetracker_url_per_player,
                        headers = {'TRN-Api-Key': config['fortnitetracker_API_TOKEN']},
                        params={'account': row['acct_id'],
                                'season': config['season']
                                }
                        )
        data = response.json()
        data_api_dict = parse_data(data)
        data_api_dict['pro'] = row['pro']
        data_api_list.append(data_api_dict.copy())

        #fortniteapi.io -> Level
        # response_io = requests.get(config['fortniteapi_url'],
        #                 headers = {'Authorization': config['fortniteapi_API_TOKEN']},
        #                 params={'account': row['acct_id'],
        #                         'season': config['season']
        #                        }
        #                )
        # data_io = response_io.json()
        # data_api_dict_io = parse_data_io(data_io)
        # data_api_list.append(data_api_dict_io.copy())        

api_output = json.dumps(data_api_list)
print(api_output)

