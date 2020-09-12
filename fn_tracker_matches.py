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
    args.config = os.path.dirname(
        os.path.abspath(__file__)) + '/fortnite2influx.conf'

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
data_api_list = []

csv_file = os.path.dirname(os.path.abspath(__file__)) + '/players.csv'
with open(csv_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
       
        fortnitetracker_url_per_player = config['fortnitetracker_url'] + "/" + str(row['plattform']) + "/" + str(row['player_name']                )      
        #fortnitetracker_url_per_player = config['fortnitetracker_url'] + "/account/" + str(row['acct_id']) + "/matches"              
        
        try:
            response = requests.get(fortnitetracker_url_per_player,
                            headers = {'TRN-Api-Key': config['fortnitetracker_API_TOKEN']},
                            params={'account': row['acct_id'],'season': config['season']}
                            )
        except:
            exit('could not load page, check connection')                            
        
        try:
            jsonObject_matches = json.loads(response.text) 
        except:
            exit('No Data for ' + str(row['player_name']) + "try command: curl --request GET '"  + str(row['player_name']) + "' --header 'TRN-Api-Key: " + str(row['fortnitetracker_API_TOKEN']) + "' ")                            

        data_api = {}
        data_api['accountId'] = row['acct_id']
        data_api['name'] = row['player_name']
        data_api['mode'] = 'Season_' + str(season)
        data_api['season'] = int(season)
        data_api['platformName'] = str(row['plattform'])
        
        try:
            for data in jsonObject_matches['recentMatches']:
                try:        
                    data_api['id'] = data['id']            
                    data_api['playlist'] = data['playlist']    
                    data_api['group'] = data['playlist']    
                    data_api['kills'] = data['kills'] 
                    data_api['minutesPlayed'] = data['minutesPlayed']
                    data_api['score'] = data['score']
                    data_api['top1'] = data['top1']
                    data_api['top3'] = data['top3']
                    data_api['top5'] = data['top5']
                    data_api['top6'] = data['top5']
                    data_api['top10'] = data['top10']
                    data_api['top12'] = data['top12']
                    data_api['top25'] = data['top25']
                    data_api['matches'] = data['matches']
                    data_api['dateCollected'] = data['dateCollected']
                    #data_api['trnRating'] = data['trnRating']
                    data_api['score'] = data['score']
                    data_api['platformId'] = data['platform']
                    data_api['playlistId'] = data['playlistId']
                    data_api['playersOutlived'] = data['playersOutlived']
                    data_api_list.append(data_api.copy())
                except KeyError:
                    pass
        except KeyError:
            pass
                    
               
api_output = json.dumps(data_api_list)
print(api_output)

