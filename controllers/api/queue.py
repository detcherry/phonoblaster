import logging
from django.utils import simplejson as json

from controllers.base import BaseHandler
from models.api.station import StationApi

class GetQueueHandler(BaseHandler):
	def get(self):
		logging.info("get queue request")
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		queue = station_proxy.queue
		self.response.out.write(json.dumps(queue))
		
		
