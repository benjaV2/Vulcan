from django.apps import AppConfig
from rst_api import views


class RstApiConfig(AppConfig):
    name = 'rst_api'

    def ready(self):
        views.init_db()
