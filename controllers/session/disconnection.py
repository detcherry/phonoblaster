import logging
from datetime import datetime
from datetime import timedelta
from django.utils import simplejson

from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.db.session import Session
from models.interface.station import InterfaceStation
from google.appengine.api.taskqueue import Task

class ChannelDisconnectionHandler(webapp.RequestHandler):
	def post(self):
		client_id = self.request.get('from')
		logging.info("%s cannot receive messages anymore" %(client_id))
		
		session = Session.all().filter("channel_id", client_id).get()
		station_key = Session.station.get_value_for_datastore(session)
		
		station_proxy = InterfaceStation(station_key = station_key)
		station_proxy.end_session(session)
		
		#Send everyone a message that a listener has left the room
		listener_delete_data = {
			"type":"listener_delete",
			"content": [],
		}
		excluded_channel_id = None
		task = Task(
			url = "/taskqueue/notify",
			params = { 
				"station_key": str(station_key),
				"data": simplejson.dumps(listener_delete_data),
				"excluded_channel_id": excluded_channel_id,
			},
		)
		task.add(
			queue_name = "listener-queue-1"
		)
		
		
application = webapp.WSGIApplication([
	(r"/_ah/channel/disconnected/", ChannelDisconnectionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
