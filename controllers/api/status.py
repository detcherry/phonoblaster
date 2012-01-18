import logging
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi

class ApiStatusHandler(BaseHandler):
	@login_required
	def post(self):
		shortname = self.request.get("shortname")
		content = self.request.get("content")
		
		authorized_status = [
			"connected",
			"commenting",
			"searching",
			"looking at people suggestions",
			"looking at its favorite tracks",
			"looking at its latest broadcasts",
		]
		
		if(content in authorized_status):
			logging.info("taskqueue sent")
			
			status_data = {
				"entity": "status",
				"event": "new",
				"content": content,
			}
		
			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(status_data)
				}
			)
			task.add(queue_name="status-queue")
			
		
		
				