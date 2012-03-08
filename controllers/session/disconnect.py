import logging
import re
from datetime import datetime

import django_setup
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task

from controllers import config
from models.api.station import StationApi

class DisconnectHandler(webapp.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s cannot receive messages anymore" %(channel_id))
		
		# Init station proxy
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		
		extended_session = station_proxy.remove_from_sessions(channel_id)
		
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
		

application = webapp.WSGIApplication([
	(r"/_ah/channel/disconnected/", DisconnectHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()