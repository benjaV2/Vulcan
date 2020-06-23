from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import io, zipfile
import json
import logging
from pymongo import MongoClient


VULNER_URL = "https://vulners.com/api/v3"
API_KEY = "9ZHMPEBGCOUKH389H29X41S6P99C9LRMVME1RQ7088IG0U6FOT3WDBM2VW7OND4T"

# Create your views here.

logger = logging.getLogger(__file__)

def serialize_plugin(raw_plugin):
    plugin = {}
    plugin['PluginID'] = raw_plugin['_source']['PluginID']
    plugin['published'] = raw_plugin['_source']['published']
    plugin['title'] = raw_plugin['_source']['title']
    plugin['cvelist'] = raw_plugin['_source']['cvelist']
    plugin['score'] = raw_plugin['score']
    return plugin


class plugin_fetcher(APIView):
    def get(self, request):
        logger.info("starting plugin listing")
        print("I'm in")
        response = requests.get(VULNER_URL + "/archive/collection/?type=nessus", params={'apiKey': API_KEY})
        logger.info("plugin json zip filed fetched")
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_files:
            for zip_file in zip_files.infolist():
                rs = json.load(zip_files.open(zip_file))
        logger.info("json plugin file extracted")
        mongo_payload = [serialize_plugin(plugin) for plugin in rs]
        logger.info("mngo payload ready")
        client = MongoClient('10.0.130.73', 27017)
        table = client.URL.plugins
        table.insert_many(mongo_payload)
        logger.info("db write operation success")
        return Response(200)






