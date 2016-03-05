from bs4 import BeautifulSoup
from os import path
import json
import codecs
import collections
import requests

trees = dict()

if not path.isfile("baumnamen.json"):
    db = json.load(codecs.open('re_strassenbaeume.geojson', encoding='utf-8'), object_pairs_hook=collections.OrderedDict)

    for f in db["features"]:
        prop = f["properties"]

        botanical_name = prop["art_bot"] or ""
        genus = prop["gattung"] or ""
        german_name = prop["art_dtsch"] or ""

        tree = { 
            "german_name": german_name.lower(), 
            "botanical_name": botanical_name.lower(), 
            "genus": genus.lower() 
        }

        trees[botanical_name.lower()] = tree

    fp = open("baumnamen.json", "w")
    json.dump(trees, fp, indent=4, sort_keys=True)
    fp.close()
else:
    trees = json.load(codecs.open('baumnamen.json', encoding='utf-8'), object_pairs_hook=collections.OrderedDict)

r = requests.get("https://wikidata.org")
soup = BeautifulSoup(r.text)

search_field = soup.select('.ui-suggester-input')
print(search_field)
