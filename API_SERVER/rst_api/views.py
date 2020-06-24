from django.shortcuts import render
from rest_framework.views import APIView
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


def init_db():
    logger.info("starting init db")
    response = requests.get(VULNER_URL + "/archive/collection/?type=nessus", params={'apiKey': API_KEY})
    logger.info("plugin json zip filed fetched")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_files:
        for zip_file in zip_files.infolist():
            rs = json.load(zip_files.open(zip_file))
    logger.info("json plugin file extracted")
    mongo_payload = [serialize_plugin(plugin) for plugin in rs]
    logger.info("mongo payload ready")
    client = MongoClient(MONGO_URL, 27017)
    table = client.URL.plugins
    table.insert_many(mongo_payload)
    logger.info("db write operation success")


@api_view(('GET',))
def plugin_get_all(request, order):
    logger.info(f'fetching all plugins')
    client = MongoClient(MONGO_URL, 27017)
    table = client.URL.plugins
    if order != '':
        if order in ['pluginID', 'score', 'published']:
            cursor = table.find({}, {"_id": False}).sort(order, 1)
        else:
            return  Response("bad order key")
    else:
        cursor = table.find({}, {"_id": False})
    logger.info(f'all plugins fetched')
    return Response([x for x in cursor])


@api_view(('GET',))
def plugin_search_by_id(request, plugin_id):
    logger.info(f'Searching for plugin {plugin_id}')
    client = MongoClient(MONGO_URL, 27017)
    table = client.URL.plugins
    cursor = table.find({"pluginID": plugin_id}, {"_id": False})
    logger.info(f'plugin {plugin_id} fetched')
    return Response([x for x in cursor])


@api_view(('GET',))
def plugin_search_by_cve(request, cve):
    logger.info(f'Searching for plugins with cve {cve}')
    client = MongoClient(MONGO_URL, 27017)
    table = client.URL.plugins
    cursor = table.find({"cvelist": cve}, {"_id": False})
    logger.info(f'plugins with cve {cve} fetched')
    return Response([x for x in cursor])






