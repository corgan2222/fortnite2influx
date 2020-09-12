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


data_api_lt = {}
data_api_lt_solo = {}
data_api_lt_duo = {}
data_api_lt_squad = {}
data_api_lt_ltm = {}
data_api_s_solo = {}
data_api_s_duo = {}
data_api_s_squad = {}
data_api_s_ltm = {}

def parse_data_lifetime(data):
    try:
        data_api_lt['name'] = data['epicUserHandle']
        data_api_lt['accountId'] = data['accountId']        
        data_api_lt['avatar'] = data['avatar']
        data_api_lt['platformId'] = data['platformId']
        data_api_lt['platformName'] = data['platformName']
        data_api_lt['platformNameLong'] = data['platformNameLong']
        data_api_lt['season'] = int(season)
        data_api_lt['mode'] = 'Lifetime'
        data_api_lt['group'] = 'all'

        data_api_lt['placetop1'] = int(data['lifeTimeStats'][8]['value'])
        data_api_lt['placetop3'] = int(data['lifeTimeStats'][1]['value'])
        data_api_lt['placetop5'] = int(data['lifeTimeStats'][0]['value'])
        data_api_lt['placetop6'] = int(data['lifeTimeStats'][2]['value'])
        data_api_lt['placetop10'] = int(data['lifeTimeStats'][3]['value'])
        data_api_lt['placetop12'] = int(data['lifeTimeStats'][4]['value'])
        data_api_lt['placetop25'] = int(data['lifeTimeStats'][5]['value'])

        score_tmp = data['lifeTimeStats'][6]['value']
        score_float = float(score_tmp.replace(',', '.'))
        data_api_lt['score'] = score_float

        data_api_lt['kd'] = float(data['lifeTimeStats'][11]['value'])

        win_tmp = data['lifeTimeStats'][9]['value']
        win_percent = float(win_tmp.replace('%', ''))

        data_api_lt['winrate'] = win_percent
        data_api_lt['wins'] = int(data['lifeTimeStats'][8]['value'])
        data_api_lt['kills'] = int(data['lifeTimeStats'][10]['value'])
        data_api_lt['matchesplayed'] = int(data['lifeTimeStats'][7]['value'])
        data_api_lt['killsPerMin'] = float(data['lifeTimeStats'][11]['value'])
    except KeyError:
        pass
    return data_api_lt

def parse_data_lifetime_solo(data):
    try:
        data_api_lt_solo['platformId'] = data['platformId']
        data_api_lt_solo['platformName'] = data['platformName']
        data_api_lt_solo['platformNameLong'] = data['platformNameLong']        
        data_api_lt_solo['name'] = data['epicUserHandle']
        data_api_lt_solo['accountId'] = data['accountId']
        data_api_lt_solo['mode'] = 'Lifetime'
        data_api_lt_solo['group'] = 'Solo'

        data_api_lt_solo['wins'] = int(data['stats']['p2']['top1']['value'])
        data_api_lt_solo['placetop1'] = int(data['stats']['p2']['top1']['value'])
        data_api_lt_solo['placetop3'] = int(data['stats']['p2']['top3']['value'])
        data_api_lt_solo['placetop5'] = int(data['stats']['p2']['top5']['value'])
        data_api_lt_solo['placetop6'] = int(data['stats']['p2']['top6']['value'])
        data_api_lt_solo['placetop10'] = int(data['stats']['p2']['top10']['value'])
        data_api_lt_solo['placetop12'] = int(data['stats']['p2']['top12']['value'])
        data_api_lt_solo['placetop25'] = int(data['stats']['p2']['top25']['value'])
        data_api_lt_solo['kd'] = float(data['stats']['p2']['kd']['value'])
        data_api_lt_solo['winrate'] = float(data['stats']['p2']['winRatio']['value'])
        data_api_lt_solo['kills'] = int(data['stats']['p2']['kills']['value'])
        data_api_lt_solo['matchesplayed'] = int(data['stats']['p2']['matches']['value'])
        data_api_lt_solo['minutesplayed'] = int(data['stats']['p2']['minutesPlayed']['value'])
        data_api_lt_solo['score'] = float(data['stats']['p2']['score']['value'])
        data_api_lt_solo['kpm'] = float(data['stats']['p2']['kpm']['value'])
        data_api_lt_solo['kpg'] = float(data['stats']['p2']['kpg']['value'])
        data_api_lt_solo['scorePerMatch'] = float(data['stats']['p2']['scorePerMatch']['value'])
        data_api_lt_solo['scorePerMin'] = float(data['stats']['p2']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_lt_solo       

def parse_data_lifetime_duo(data):
    try:
        data_api_lt_duo['platformId'] = data['platformId']
        data_api_lt_duo['platformName'] = data['platformName']
        data_api_lt_duo['platformNameLong'] = data['platformNameLong']        
        data_api_lt_duo['name'] = data['epicUserHandle']
        data_api_lt_duo['accountId'] = data['accountId']
        data_api_lt_duo['mode'] = 'Lifetime'
        data_api_lt_duo['group'] = 'Duo'

        data_api_lt_duo['wins'] = int(data['stats']['p10']['top1']['value'])
        data_api_lt_duo['placetop1'] = int(data['stats']['p10']['top1']['value'])
        data_api_lt_duo['placetop3'] = int(data['stats']['p10']['top3']['value'])
        data_api_lt_duo['placetop5'] = int(data['stats']['p10']['top5']['value'])
        data_api_lt_duo['placetop6'] = int(data['stats']['p10']['top6']['value'])
        data_api_lt_duo['placetop10'] = int(data['stats']['p10']['top10']['value'])
        data_api_lt_duo['placetop12'] = int(data['stats']['p10']['top12']['value'])
        data_api_lt_duo['placetop25'] = int(data['stats']['p10']['top25']['value'])
        data_api_lt_duo['kd'] = float(data['stats']['p10']['kd']['value'])
        data_api_lt_duo['winrate'] = float(data['stats']['p10']['winRatio']['value'])
        data_api_lt_duo['kills'] = int(data['stats']['p10']['kills']['value'])
        data_api_lt_duo['matchesplayed'] = int(data['stats']['p10']['matches']['value'])
        data_api_lt_duo['minutesplayed'] = int(data['stats']['p10']['minutesPlayed']['value'])
        data_api_lt_duo['score'] = float(data['stats']['p10']['score']['value'])
        data_api_lt_duo['kpm'] = float(data['stats']['p10']['kpm']['value'])
        data_api_lt_duo['kpg'] = float(data['stats']['p10']['kpg']['value'])
        data_api_lt_duo['scorePerMatch'] = float(data['stats']['p10']['scorePerMatch']['value'])
        data_api_lt_duo['scorePerMin'] = float(data['stats']['p10']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_lt_duo


def parse_data_lifetime_squad(data):
    try:
        data_api_lt_squad['platformId'] = data['platformId']
        data_api_lt_squad['platformName'] = data['platformName']
        data_api_lt_squad['platformNameLong'] = data['platformNameLong']        
        data_api_lt_squad['name'] = data['epicUserHandle']
        data_api_lt_squad['accountId'] = data['accountId']
        data_api_lt_squad['mode'] = 'Lifetime'
        data_api_lt_squad['group'] = 'Squad'

        data_api_lt_squad['wins'] = int(data['stats']['p9']['top1']['value'])
        data_api_lt_squad['placetop1'] = int(data['stats']['p9']['top1']['value'])
        data_api_lt_squad['placetop3'] = int(data['stats']['p9']['top3']['value'])
        data_api_lt_squad['placetop5'] = int(data['stats']['p9']['top5']['value'])
        data_api_lt_squad['placetop6'] = int(data['stats']['p9']['top6']['value'])
        data_api_lt_squad['placetop10'] = int(data['stats']['p9']['top10']['value'])
        data_api_lt_squad['placetop12'] = int(data['stats']['p9']['top12']['value'])
        data_api_lt_squad['placetop25'] = int(data['stats']['p9']['top25']['value'])
        data_api_lt_squad['kd'] = float(data['stats']['p9']['kd']['value'])
        data_api_lt_squad['winrate'] = float(data['stats']['p9']['winRatio']['value'])
        data_api_lt_squad['kills'] = int(data['stats']['p9']['kills']['value'])
        data_api_lt_squad['matchesplayed'] = int(data['stats']['p9']['matches']['value'])
        data_api_lt_squad['minutesplayed'] = int(data['stats']['p9']['minutesPlayed']['value'])
        data_api_lt_squad['score'] = float(data['stats']['p9']['score']['value'])
        data_api_lt_squad['kpm'] = float(data['stats']['p9']['kpm']['value'])
        data_api_lt_squad['kpg'] = float(data['stats']['p9']['kpg']['value'])
        data_api_lt_squad['scorePerMatch'] = float(data['stats']['p9']['scorePerMatch']['value'])
        data_api_lt_squad['scorePerMin'] = float(data['stats']['p9']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_lt_squad

def parse_data_lifetime_ltm(data):
    try:
        data_api_lt_ltm['platformId'] = data['platformId']
        data_api_lt_ltm['platformName'] = data['platformName']
        data_api_lt_ltm['platformNameLong'] = data['platformNameLong']        
        data_api_lt_ltm['name'] = data['epicUserHandle']
        data_api_lt_ltm['accountId'] = data['accountId']
        data_api_lt_ltm['mode'] = 'Lifetime'
        data_api_lt_ltm['group'] = 'Ltm'

        data_api_lt_ltm['wins'] = int(data['stats']['ltm']['top1']['value'])
        data_api_lt_ltm['placetop1'] = int(data['stats']['ltm']['top1']['value'])
        data_api_lt_ltm['placetop3'] = int(data['stats']['ltm']['top3']['value'])
        data_api_lt_ltm['placetop5'] = int(data['stats']['ltm']['top5']['value'])
        data_api_lt_ltm['placetop6'] = int(data['stats']['ltm']['top6']['value'])
        data_api_lt_ltm['placetop10'] = int(data['stats']['ltm']['top10']['value'])
        data_api_lt_ltm['placetop12'] = int(data['stats']['ltm']['top12']['value'])
        data_api_lt_ltm['placetop25'] = int(data['stats']['ltm']['top25']['value'])
        data_api_lt_ltm['kd'] = float(data['stats']['ltm']['kd']['value'])
        data_api_lt_ltm['winrate'] = float(data['stats']['ltm']['winRatio']['value'])
        data_api_lt_ltm['kills'] = int(data['stats']['ltm']['kills']['value'])
        data_api_lt_ltm['matchesplayed'] = int(data['stats']['ltm']['matches']['value'])
        data_api_lt_ltm['minutesplayed'] = int(data['stats']['ltm']['minutesPlayed']['value'])
        data_api_lt_ltm['score'] = float(data['stats']['ltm']['score']['value'])
        data_api_lt_ltm['kpm'] = float(data['stats']['ltm']['kpm']['value'])
        data_api_lt_ltm['kpg'] = float(data['stats']['ltm']['kpg']['value'])
        data_api_lt_ltm['scorePerMatch'] = float(data['stats']['ltm']['scorePerMatch']['value'])
        data_api_lt_ltm['scorePerMin'] = float(data['stats']['ltm']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_lt_ltm


def parse_data_season_solo(data):
    try:
        data_api_s_solo['platformId'] = data['platformId']
        data_api_s_solo['platformName'] = data['platformName']
        data_api_s_solo['platformNameLong'] = data['platformNameLong']        
        data_api_s_solo['name'] = data['epicUserHandle']
        data_api_s_solo['accountId'] = data['accountId']
        data_api_s_solo['mode'] = 'Season_' + str(season)
        data_api_s_solo['group'] = 'Solo'

        data_api_s_solo['wins'] = int(data['stats']['curr_p2']['top1']['value'])
        data_api_s_solo["placetop1"] = int(data['stats']['curr_p2']['top1']['value'])
        data_api_s_solo["placetop3"] = int(data['stats']['curr_p2']['top3']['value'])
        data_api_s_solo["placetop5"] = int(data['stats']['curr_p2']['top5']['value'])
        data_api_s_solo["placetop6"] = int(data['stats']['curr_p2']['top6']['value'])
        data_api_s_solo["placetop10"] = int(data['stats']['curr_p2']['top10']['value'])
        data_api_s_solo["placetop12"] = int(data['stats']['curr_p2']['top12']['value'])
        data_api_s_solo["placetop25"] = int(data['stats']['curr_p2']['top25']['value'])
        data_api_s_solo["kd"] = float(data['stats']['curr_p2']['kd']['value'])
        data_api_s_solo["winrate"] = float(data['stats']['curr_p2']['winRatio']['value'])
        data_api_s_solo["kills"] = int(data['stats']['curr_p2']['kills']['value'])
        data_api_s_solo["matchesplayed"] = int(data['stats']['curr_p2']['matches']['value'])
        data_api_s_solo["minutesplayed"] = int(data['stats']['curr_p2']['minutesPlayed']['value'])
        data_api_s_solo["score"] = float(data['stats']['curr_p2']['score']['value'])
        data_api_s_solo["kpm"] = float(data['stats']['curr_p2']['kpm']['value'])
        data_api_s_solo["kpg"] = float(data['stats']['curr_p2']['kpg']['value'])
        data_api_s_solo["scorePerMatch"] = float(data['stats']['curr_p2']['scorePerMatch']['value'])
        data_api_s_solo["scorePerMin"] = float(data['stats']['curr_p2']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_s_solo


def parse_data_season_duo(data):
    try:
        data_api_s_duo['platformId'] = data['platformId']
        data_api_s_duo['platformName'] = data['platformName']
        data_api_s_duo['platformNameLong'] = data['platformNameLong']        
        data_api_s_duo['name'] = data['epicUserHandle']
        data_api_s_duo['accountId'] = data['accountId']
        data_api_s_duo['mode'] = 'Season_' + str(season)
        data_api_s_duo['group'] = 'Duo'

        data_api_s_duo["wins"] = int(data['stats']['curr_p10']['top1']['value'])
        data_api_s_duo["placetop1"] = int(data['stats']['curr_p10']['top1']['value'])
        data_api_s_duo["placetop3"] = int(data['stats']['curr_p10']['top3']['value'])
        data_api_s_duo["placetop5"] = int(data['stats']['curr_p10']['top5']['value'])
        data_api_s_duo["placetop6"] = int(data['stats']['curr_p10']['top6']['value'])
        data_api_s_duo["placetop10"] = int(data['stats']['curr_p10']['top10']['value'])
        data_api_s_duo["placetop12"] = int(data['stats']['curr_p10']['top12']['value'])
        data_api_s_duo["placetop25"] = int(data['stats']['curr_p10']['top25']['value'])
        data_api_s_duo["kd"] = float(data['stats']['curr_p10']['kd']['value'])
        data_api_s_duo["winrate"] = float(data['stats']['curr_p10']['winRatio']['value'])
        data_api_s_duo["kills"] = int(data['stats']['curr_p10']['kills']['value'])
        data_api_s_duo["matchesplayed"] = int(data['stats']['curr_p10']['matches']['value'])
        data_api_s_duo["minutesplayed"] = int(data['stats']['curr_p10']['minutesPlayed']['value'])
        data_api_s_duo["score"] = float(data['stats']['curr_p10']['score']['value'])
        data_api_s_duo["kpm"] = float(data['stats']['curr_p10']['kpm']['value'])
        data_api_s_duo["kpg"] = float(data['stats']['curr_p10']['kpg']['value'])
        data_api_s_duo["scorePerMatch"] = float(data['stats']['curr_p10']['scorePerMatch']['value'])
        data_api_s_duo["scorePerMin"] = float(data['stats']['curr_p10']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_s_duo

def parse_data_season_squad(data):
    try:
        data_api_s_squad['platformId'] = data['platformId']
        data_api_s_squad['platformName'] = data['platformName']
        data_api_s_squad['platformNameLong'] = data['platformNameLong']        
        data_api_s_squad['name'] = data['epicUserHandle']
        data_api_s_squad['accountId'] = data['accountId']
        data_api_s_squad['mode'] = 'Season_' + str(season)
        data_api_s_squad['group'] = 'Squad'

        data_api_s_squad["wins"] = int(data['stats']['curr_p9']['top1']['value'])
        data_api_s_squad["placetop1"] = int(data['stats']['curr_p9']['top1']['value'])
        data_api_s_squad["placetop3"] = int(data['stats']['curr_p9']['top3']['value'])
        data_api_s_squad["placetop5"] = int(data['stats']['curr_p9']['top5']['value'])
        data_api_s_squad["placetop6"] = int(data['stats']['curr_p9']['top6']['value'])
        data_api_s_squad["placetop10"] = int(data['stats']['curr_p9']['top10']['value'])
        data_api_s_squad["placetop12"] = int(data['stats']['curr_p9']['top12']['value'])
        data_api_s_squad["placetop25"] = int(data['stats']['curr_p9']['top25']['value'])
        data_api_s_squad["kd"] = float(data['stats']['curr_p9']['kd']['value'])
        data_api_s_squad["winrate"] = float(data['stats']['curr_p9']['winRatio']['value'])
        data_api_s_squad["kills"] = int(data['stats']['curr_p9']['kills']['value'])
        data_api_s_squad["matchesplayed"] = int(data['stats']['curr_p9']['matches']['value'])
        data_api_s_squad["minutesplayed"] = int(data['stats']['curr_p9']['minutesPlayed']['value'])
        data_api_s_squad["score"] = float(data['stats']['curr_p9']['score']['value'])
        data_api_s_squad["kpm"] = float(data['stats']['curr_p9']['kpm']['value'])
        data_api_s_squad["kpg"] = float(data['stats']['curr_p9']['kpg']['value'])
        data_api_s_squad["scorePerMatch"] = float(data['stats']['curr_p9']['scorePerMatch']['value'])
        data_api_s_squad["scorePerMin"] = float(data['stats']['curr_p9']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_s_squad

def parse_data_season_ltm(data):
    try:
        data_api_s_ltm['platformId'] = data['platformId']
        data_api_s_ltm['platformName'] = data['platformName']
        data_api_s_ltm['platformNameLong'] = data['platformNameLong']        
        data_api_s_ltm['name'] = data['epicUserHandle']
        data_api_s_ltm['accountId'] = data['accountId']
        data_api_s_ltm['mode'] = 'Season_' + str(season)
        data_api_s_ltm['group'] = 'Ltm'

        data_api_s_ltm["wins"] = int(data['stats']['curr_ltm']['top1']['value'])
        data_api_s_ltm["placetop1"] = int(data['stats']['curr_ltm']['top1']['value'])
        data_api_s_ltm["placetop3"] = int(data['stats']['curr_ltm']['top3']['value'])
        data_api_s_ltm["placetop5"] = int(data['stats']['curr_ltm']['top5']['value'])
        data_api_s_ltm["placetop6"] = int(data['stats']['curr_ltm']['top6']['value'])
        data_api_s_ltm["placetop10"] = int(data['stats']['curr_ltm']['top10']['value'])
        data_api_s_ltm["placetop12"] = int(data['stats']['curr_ltm']['top12']['value'])
        data_api_s_ltm["placetop25"] = int(data['stats']['curr_ltm']['top25']['value'])
        data_api_s_ltm["kd"] = float(data['stats']['curr_ltm']['kd']['value'])
        data_api_s_ltm["winrate"] = float(data['stats']['curr_ltm']['winRatio']['value'])
        data_api_s_ltm["kills"] = int(data['stats']['curr_ltm']['kills']['value'])
        data_api_s_ltm["matchesplayed"] = int(data['stats']['curr_ltm']['matches']['value'])
        data_api_s_ltm["minutesplayed"] = int(data['stats']['curr_ltm']['minutesPlayed']['value'])
        data_api_s_ltm["score"] = float(data['stats']['curr_ltm']['score']['value'])
        data_api_s_ltm["kpm"] = float(data['stats']['curr_ltm']['kpm']['value'])
        data_api_s_ltm["kpg"] = float(data['stats']['curr_ltm']['kpg']['value'])
        data_api_s_ltm["scorePerMatch"] = float(data['stats']['curr_ltm']['scorePerMatch']['value'])
        data_api_s_ltm["scorePerMin"] = float(data['stats']['curr_ltm']['scorePerMin']['value'])
    except KeyError:
        pass
    return data_api_s_ltm


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
        
       
        data_api_dict_lt = parse_data_lifetime(data)
        
        data_api_dict_lt_solo = parse_data_lifetime_solo(data)
        data_api_dict_lt_duo = parse_data_lifetime_duo(data)
        data_api_dict_lt_squad = parse_data_lifetime_squad(data)
        data_api_dict_lt_ltm = parse_data_lifetime_ltm(data)
        
        data_api_dict_s_solo = parse_data_season_solo(data)
        data_api_dict_s_duo = parse_data_season_duo(data)
        data_api_dict_s_squad = parse_data_season_squad(data)
        data_api_dict_s_ltm = parse_data_season_ltm(data)
        

        data_api_dict_lt['pro'] = row['pro']
        data_api_dict_lt_solo['pro'] = row['pro']
        data_api_dict_lt_duo['pro'] = row['pro']
        data_api_dict_lt_squad['pro'] = row['pro']
        data_api_dict_s_solo['pro'] = row['pro']
        data_api_dict_s_duo['pro'] = row['pro']
        data_api_dict_s_squad['pro'] = row['pro']        
        data_api_dict_s_ltm['pro'] = row['pro']        
        data_api_dict_lt_ltm['pro'] = row['pro']        

        data_api_list.append(data_api_dict_lt.copy())
        data_api_list.append(data_api_dict_lt_solo.copy())
        data_api_list.append(data_api_dict_lt_duo.copy())
        data_api_list.append(data_api_dict_lt_squad.copy())
        data_api_list.append(data_api_dict_s_solo.copy())
        data_api_list.append(data_api_dict_s_duo.copy())
        data_api_list.append(data_api_dict_s_squad.copy())
        data_api_list.append(data_api_dict_s_ltm.copy())
        data_api_list.append(data_api_dict_lt_ltm.copy())
   

api_output = json.dumps(data_api_list)
print(api_output)

