import logging
import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler

from models.api.station import StationApi

class ApiViewsHandler(BaseHandler):
	def post(self):
		shortname = self.request.get("shortname")		
		station_proxy = StationApi(shortname)
		station_proxy.increment_views_counter()		