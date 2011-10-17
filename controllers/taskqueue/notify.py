import logging

from datetime import datetime
from datetime import timedelta
from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import channel
from google.appengine.ext import db

from models.interface.station import InterfaceStation

class NotificationHandler(webapp.RequestHandler):
	def post(self):
		self.station_key = db.Key(self.request.get("station_key"))
		self.json = self.request.get("data")
		self.excluded_channel_id = self.request.get("excluded_channel_id")
		
		# Get active sessions
		station_proxy = InterfaceStation(station_key = self.station_key)
		active_sessions = station_proxy.station_sessions
		
		if(self.excluded_channel_id):
			# Send message to everybody except the excluded channel
			for session in active_sessions:
				if(session.channel_id != self.excluded_channel_id):
					channel.send_message(session.channel_id, self.json)	
		else:
			# Send message to everybody
			for session in active_sessions:
				channel.send_message(session.channel_id, self.json)
		
		

application = webapp.WSGIApplication([
	(r"/taskqueue/notify", NotificationHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()