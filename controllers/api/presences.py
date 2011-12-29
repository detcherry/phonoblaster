import logging
from django.utils import simplejson as json

from controllers.base import BaseHandler
from models.api.station import StationApi

class GetPresencesHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		presences = station_proxy.presences
		self.response.out.write(json.dumps(presences))