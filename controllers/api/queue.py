import logging
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi

class ApiQueueHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		
		station_proxy = StationApi(shortname)
		queue = station_proxy.queue
		
		self.response.out.write(json.dumps(queue))
	
	@login_required
	def post(self):
		shortname = self.request.get("shortname")
		new_broadcast = json.loads(self.request.get("broadcast"))
		station_proxy = StationApi(shortname)
		self.station = station_proxy.station
		self.user = self.user_proxy.user
		
		extended_broadcast = None
		if(self.user_proxy.is_admin_of(self.station.key().name())):
			extended_broadcast = station_proxy.add_to_queue(new_broadcast, self.user, True)
			
		response = False
		if(extended_broadcast):
			# Add a taskqueue to warn everyone
			new_broadcast_data = {
				"event": "new-broadcast",
				"content": extended_broadcast,
			}

			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(new_broadcast_data)
				}
			)
			task.add(queue_name="broadcasts-queue")
			response = True

		self.response.out.write(json.dumps({ "response": response }))
		