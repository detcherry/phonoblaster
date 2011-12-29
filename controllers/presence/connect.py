import logging
import re
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from controllers import config
from models.api.station import StationApi
from google.appengine.api.taskqueue import Task

class PresenceConnectHandler(webapp.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s is ready to receive messages" %(channel_id))
		
		# Init station proxy, add presence 
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		extended_presence = station_proxy.add_presence(channel_id)
		
		# Add a taskqueue to warn everyone
		new_presence_data = {
			"event": "new-presence",
			"content": extended_presence,
		}
		task = Task(
			url = "/taskqueue/multicast",
			params = {
				"station": config.VERSION + "-" + shortname,
				"data": json.dumps(new_presence_data)
			}
		)
		task.add(queue_name="presence-queue")


application = webapp.WSGIApplication([
	(r"/_ah/channel/connected/", PresenceConnectHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()