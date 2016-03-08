import json
import io
import requests
from os import path

BASE_URL = "https://wdq.wmflabs.org/api"

trees = {}

if path.exists('trees.json'):
    trees = json.load(open('trees.json', 'r'))

stream = io.open('re_strassenbaeume.geojson', 'r', encoding='utf-8')
db = json.load(stream)

for f in db["features"]:
    prop = f["properties"]

    botanical_name = prop["art_bot"].lower() or ""
    
    if len(botanical_name) == 0:
        continue

    query = "STRING[225:\"{}\"]".format(botanical_name.capitalize())
    payload = {
        "q": query,
        "format": 'json',
    }

    response = requests.get(BASE_URL, params=payload)
    json_response = response.json()

    if json_response['status']['error'] == "OK":
        tree = {
            'wd_item_id': json_response['items'][0]
        }

        

        if botanical_name not in trees.keys():
            trees[botanical_name] = tree

json.dump(trees, open("trees.json", "w"))
