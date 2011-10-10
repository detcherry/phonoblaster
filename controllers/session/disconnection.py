import logging
from datetime import datetime
from datetime import timedelta
from django.utils import simplejson

from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.db.session import Session
from models.notifiers.notifier import Notifier

class ChannelDisconnectionHandler(webapp.RequestHandler):
	def post(self):
		client_id = self.request.get('from')
		logging.info("%s cannot receive messages anymore" %(client_id))
		
		session = Session.all().filter("channel_id", client_id).get()
		
		station_left = session.station
		
		session.ended = datetime.now()
		session.put()
		logging.info("Station %s doesn't feed this channel anymore" %(session.station.identifier))
		
		#Send everyone a message that a listener has left the room
		listener_delete_data = {
			"type":"listener_delete",
			"content": [],
		}
		notifier = Notifier(station_left.key(), listener_delete_data, None)
		notifier.send()
		
		
		
application = webapp.WSGIApplication([
	(r"/_ah/channel/disconnected/", ChannelDisconnectionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
