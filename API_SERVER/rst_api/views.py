from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import io, zipfile
import json
import pymongo


VULNER_URL = "https://vulners.com/api/v3"
API_KEY = "9ZHMPEBGCOUKH389H29X41S6P99C9LRMVME1RQ7088IG0U6FOT3WDBM2VW7OND4T"

# Create your views here.


class plugin_fetcher(APIView):
    def get(self, request):
        print("I'm IN!")
        response = requests.get(VULNER_URL + "/archive/collection/?type=nessus", params={'apiKey': API_KEY})
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_files:
            for zip_file in zip_files.infolist():
                rs = json.load(zip_files.open(zip_file))
        return Response(rs)






