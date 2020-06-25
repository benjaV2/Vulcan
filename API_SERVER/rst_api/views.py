from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
import io, zipfile
import json, os
import logging
from pymongo import MongoClient


VULNER_URL = os.environ.get("VULNER_API", "https://vulners.com/api/v3")
API_KEY = os.environ.get("API_KEY", "9ZHMPEBGCOUKH389H29X41S6P99C9LRMVME1RQ7088IG0U6FOT3WDBM2VW7OND4T")
MONGO_URL = os.environ.get("MONGO_URL", "10.0.130.73")
PLUGIN_TYPE = "nessus"

# Create your views here.

logger = logging.getLogger("Views.py")
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def serialize_plugin(raw_plugin):
    plugin = {}
    source_key_list = ["pluginID", "published", "title", "cvelist"]
    for key in source_key_list:
        plugin[key] = raw_plugin["_source"].get(key)
    plugin['score'] = raw_plugin['score']
    return plugin


def fetch_and_extract_plugin_file():
    response = requests.get(f"{VULNER_URL}/archive/collection/?type={PLUGIN_TYPE}", params={'apiKey': API_KEY})
    logger.info("plugin json zip filed fetched")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_files:
        for zip_file in zip_files.infolist():
            rs = json.load(zip_files.open(zip_file))
    logger.info("json plugin file extracted")
    return rs


def check_db(client):
    db = client.plugins
    collection_names = db.collection_names()
    if PLUGIN_TYPE in collection_names:
        return True
    return False

def init_db():
    client = MongoClient(MONGO_URL, 27017)
    if check_db(client):
        logger.info("db already initiated. skipping...")
        return
    logger.info("starting init db")
    rs = fetch_and_extract_plugin_file()
    mongo_payload = [serialize_plugin(plugin) for plugin in rs]
    logger.info(f"mongo payload ready. inserting to {MONGO_URL}")
    table = client.plugins[PLUGIN_TYPE]
    table.insert_many(mongo_payload)
    table.create_index([('pluginID', 1)], unique=True, name="pluginID")
    logger.info("db write operation success")


def update_db():
    logger.info("starting update db")
    rs = fetch_and_extract_plugin_file()
    mongo_payload = [serialize_plugin(plugin) for plugin in rs]
    logger.info(f"mongo payload ready. updating {MONGO_URL}")
    client = MongoClient(MONGO_URL, 27017)
    table = client.plugins[PLUGIN_TYPE]
    for plugin in mongo_payload:
        table.update({"pluginID": plugin["pluginID"]}, plugin, True)
    logger.info("db update operation success")


@api_view(('GET',))
def plugin_get_all(request, order):
    logger.info(f'fetching all plugins')
    client = MongoClient(MONGO_URL, 27017)
    table = client.plugins[PLUGIN_TYPE]
    if order != '':
        if order in ['pluginID', 'score', 'published']:
            cursor = table.find({}, {"_id": False}).sort(order, 1)
        else:
            return Response("bad order key")
    else:
        cursor = table.find({}, {"_id": False})
    logger.info(f'all plugins fetched')
    return Response([x for x in cursor])


@api_view(('GET',))
def plugin_search_by_id(request, plugin_id):
    logger.info(f'Searching for plugin {plugin_id}')
    client = MongoClient(MONGO_URL, 27017)
    table = client.plugins[PLUGIN_TYPE]
    cursor = table.find({"pluginID": plugin_id}, {"_id": False})
    logger.info(f'plugin {plugin_id} fetched')
    return Response([x for x in cursor])


@api_view(('GET',))
def plugin_search_by_cve(request, cve):
    logger.info(f'Searching for plugins with cve {cve}')
    client = MongoClient(MONGO_URL, 27017)
    table = client.plugins[PLUGIN_TYPE]
    cursor = table.find({"cvelist": cve}, {"_id": False, "cvelist": False})
    logger.info(f'plugins with cve {cve} fetched')
    return Response([x for x in cursor])
