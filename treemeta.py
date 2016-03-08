import json
import io
import requests
from os import path
from tqdm import *
import time

BASE_URL = "https://wdq.wmflabs.org/api"

trees = {}

TREEMETA_M_TIME = path.getmtime('treemeta.py')

if path.exists('trees.json'):
    trees = json.load(open('trees.json', 'r'))

stream = io.open('re_strassenbaeume.geojson', 'r', encoding='utf-8')
db = json.load(stream)

def get_wikidata_id(botanical_name):
    query = "STRING[225:\"{}\"]".format(botanical_name.capitalize())
    payload = {
        "q": query,
        "format": 'json',
    }

    response = requests.get(BASE_URL, params=payload)
    json_response = response.json()

    if json_response['status']['error'] == "OK" and len(json_response['items']) > 0:
        return json_response['items'][0]
    else:
        return 0

def get_wikidata_claims(id):
    pass

def is_current(filename):
    return not path.exists(filename) or path.getmtime(filename) < TREEMETA_M_TIME

for f in tqdm(db["features"]):
    prop = f["properties"]

    if prop['art_bot'] == None:
        continue

    botanical_name = prop["art_bot"].lower() or ""
    tree_file_name = 'data/{}.json'.format(botanical_name)
    
    if len(botanical_name) == 0 or not is_current(tree_file_name):
        continue
    
    wd_id = get_wikidata_id(botanical_name)
    if wd_id == 0:
        print("Could not fetch wikidata item for {}\n".format(botanical_name))
        continue

    tree = {
        'wd_item_id': wd_id
    }
    
    json.dump(tree, open(tree_file_name, 'w'), indent=4)

    time.sleep(3)
