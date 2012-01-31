from datetime import datetime

import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler

from models.api.station import StationApi

class ApiBroadcastsHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		
		if(station_proxy.station):
			offset = datetime.utcfromtimestamp(int(self.request.get("offset")))
			extended_broadcasts = station_proxy.get_broadcasts(offset)
		
		self.response.out.write(json.dumps(extended_broadcasts))
