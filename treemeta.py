import json
import io
import requests
from os import path
from tqdm import *
import time

WDQ_BASE_URL = "https://wdq.wmflabs.org/api"
WD_BASE_URL = "https://www.wikidata.org/w/api.php"

TREEMETA_M_TIME = path.getmtime('treemeta.py')

def get_wikidata_id(botanical_name):
    query = "STRING[225:\"{}\"]".format(botanical_name.capitalize())
    payload = {
        "q": query,
        "format": 'json',
    }

    response = requests.get(WDQ_BASE_URL, params=payload)
    json_response = response.json()

    if json_response['status']['error'] == "OK" and len(json_response['items']) > 0:
        return json_response['items'][0]
    else:
        return 0

def get_wikidata(id):
    query = {
        'action': 'wbgetentities',
        'ids': 'Q{}'.format(id),
        'format': 'json'
    }

    response = requests.get(WD_BASE_URL, params=query)
    json_response = response.json()

    result = {}
    if json_response['success'] == 1 and len(json_response['entities']) == 1:
        data = json_response['entities']['Q{}'.format(id)]

        aliases = data['aliases']
        if 'de' in aliases.keys():
            aliases = aliases['de']

        result = {
            'label': data['labels']['de'],
            'description': data['descriptions']['de'],
            'aliases': aliases,
            'claims': data['claims']
        }

    return result
    

def is_current(filename):
    return not path.exists(filename) or path.getmtime(filename) < TREEMETA_M_TIME

def log_failed(prop, failed):
    print "Failed: {}".format(prop['gml_id'])
    failed.append(prop['gml_id'])

if __name__ == '__main__':
    stream = io.open('re_strassenbaeume.geojson', 'r', encoding='utf-8')
    db = json.load(stream)

    if path.exists('failed.json'):
        failed = json.load(open('failed.json', 'r'))
    else:
        failed = []

    for f in tqdm(db["features"]):
        prop = f["properties"]

        if prop['gml_id'] in failed:
            continue

        if prop['art_bot'] == None:
            log_failed(prop, failed)    
            continue

        botanical_name = prop["art_bot"].lower() or ""
        tree_file_name = 'data/{}.json'.format(botanical_name)
        
        if len(botanical_name) == 0 or not is_current(tree_file_name):        
            continue

        tree = {}
        if path.exists(tree_file_name):
            tree = json.load(open(tree_file_name, 'r'))
        
        if 'wd_item_id' not in tree.keys():
            wd_item_id = get_wikidata_id(botanical_name)
            
            if wd_item_id == 0:
                log_failed(prop, failed)
                continue
            else:
                tree['wd_item_id'] = wd_item_id

        tree['wd_data'] = get_wikidata(tree['wd_item_id'])
        
        json.dump(tree, open(tree_file_name, 'w'), indent=4)
        json.dump(failed, open('failed.json', 'w'), indent=4)

        time.sleep(3)
