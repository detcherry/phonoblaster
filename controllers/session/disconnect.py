import logging
import re
import json
from datetime import datetime

import webapp2
from google.appengine.api.taskqueue import Task

from controllers import config
from models.api.station import StationApi

class DisconnectHandler(webapp2.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s cannot receive messages anymore" %(channel_id))
		
		# Init station proxy
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		
		extended_session = station_proxy.remove_from_sessions(channel_id)
		
		if(extended_session):
			# Add a taskqueue to warn everyone
			session_gone_data = {
				"entity": "session",
				"event": "remove",
				"content": extended_session,
			}
			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(session_gone_data)
				}
			)
			task.add(queue_name="sessions-queue")
		