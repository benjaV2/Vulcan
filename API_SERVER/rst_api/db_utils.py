import requests
import io
import zipfile
import json
import logging
from pymongo import MongoClient
from API_SERVER.settings import MONGO_URL, PLUGIN_TYPE, API_KEY, VULNER_URL


logger = logging.getLogger("db_utils")
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
