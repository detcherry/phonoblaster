from datetime import datetime

import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler

from models.api.station import StationApi

class ApiBroadcastsHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		offset = self.request.get("offset")
		station_proxy = StationApi(shortname)

		if(station_proxy.station and offset):
			extended_broadcasts = station_proxy.get_broadcasts(datetime.utcfromtimestamp(int(offset)))
			self.response.out.write(json.dumps(extended_broadcasts))
		else:
			self.error(404)