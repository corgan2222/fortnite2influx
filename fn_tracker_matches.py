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

def parse_data(data):
    try:        
        data_api['id'] = data['id']
        data_api['dateCollected'] = data['dateCollected']
        data_api['accountId'] = data['accountId']
        data_api['kills'] = data['kills']
        data_api['matches'] = data['matches']
        data_api['playlist'] = data['playlist']
        data_api['score'] = data['score']
        data_api['top1'] = data['top1']
        data_api['top10'] = data['top10']
        data_api['top12'] = data['top12']
        data_api['top25'] = data['top25']
        data_api['top3'] = data['top3']
        data_api['top5'] = data['top5']
        data_api['top6'] = data['top6']
        data_api['trnRating'] = data['trnRating']

    except KeyError:
        pass

    return data_api


data_api_list = []

with open('players.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
       
        fortnitetracker_url_per_player = config['fortnitetracker_url'] + "/account/" + str(row['acct_id']) + '/matches'   
        print(fortnitetracker_url_per_player)   

        response = requests.get(fortnitetracker_url_per_player,headers = {'TRN-Api-Key': config['fortnitetracker_API_TOKEN']})
                        # params={'account': row['acct_id'],
                        #         'season': config['season']
                        #         }
                        # )
        data = response.json()
        print(data)
        data_api_dict = parse_data(data)
        data_api_dict['pro'] = row['pro']
        data_api_dict['account'] = row['acct_id']
        data_api_dict['player_name'] = row['player_name']
        data_api_list.append(data_api_dict.copy())

        

api_output = json.dumps(data_api_list)
print(api_output)

