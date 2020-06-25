from rest_framework.response import Response
from rest_framework.decorators import api_view
import logging
from pymongo import MongoClient
from API_SERVER.settings import MONGO_URL, PLUGIN_TYPE



# Create your views here.

logger = logging.getLogger("views")
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


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
