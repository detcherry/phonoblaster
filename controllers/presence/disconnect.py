import logging
import re
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from controllers import config
from models.api.station import StationApi
from google.appengine.api.taskqueue import Task

class PresenceDisconnectHandler(webapp.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s cannot receive messages anymore" %(channel_id))
		
		# Init station proxy, remove presence 
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		extended_presence = station_proxy.remove_presence(channel_id)

		# Add a taskqueue to warn everyone
		presence_removed_data = {
			"event": "presence-removed",
			"content": extended_presence,
		}
		task = Task(
			url = "/taskqueue/multicast",
			params = {
				"station": config.VERSION + "-" + shortname,
				"data": json.dumps(presence_removed_data)
			}
		)
		task.add(queue_name="presence-queue")


application = webapp.WSGIApplication([
	(r"/_ah/channel/disconnected/", PresenceDisconnectHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()