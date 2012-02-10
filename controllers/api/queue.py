import logging
import re
import django_setup
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
		broadcast = json.loads(self.request.get("content"))
		
		station_proxy = StationApi(shortname)
		self.station = station_proxy.station
		
		extended_broadcast = None
		if(self.user_proxy.is_admin_of(self.station.key().name())):
			extended_broadcast = station_proxy.add_to_queue(broadcast)
			
		response = False
		if(extended_broadcast):
			# Add a taskqueue to warn everyone
			broadcast_data = {
				"entity": "broadcast",
				"event": "new",
				"content": extended_broadcast,
			}

			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(broadcast_data)
				}
			)
			task.add(queue_name="broadcasts-queue")
			response = True

		self.response.out.write(json.dumps({ "response": response }))
		

class ApiQueueDeleteHandler(BaseHandler):
	
	@login_required
	def delete(self, key_name):
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)
		
		station_proxy = StationApi(shortname)
		self.station = station_proxy.station
		
		response = False
		if(self.user_proxy.is_admin_of(self.station.key().name())):
			response = station_proxy.remove_from_queue(key_name)
		
		if(response):
			broadcast_data = {
				"entity": "broadcast",
				"event": "remove",
				"content": key_name,
			}

			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(broadcast_data)
				}
			)
			task.add(queue_name="broadcasts-queue")

		self.response.out.write(json.dumps({ "response": response }))
		