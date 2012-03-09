import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler

from models.api.station import StationApi

class ApiAirHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		
		if(station_proxy.station):
			queue = station_proxy.queue
			if(queue):
				data = {
					"response": True,
					"content": queue[0],
				}
			else:
				data = {
					"response": False,
				}

			self.response.out.write(json.dumps(data))
		else:
			self.error(404)
