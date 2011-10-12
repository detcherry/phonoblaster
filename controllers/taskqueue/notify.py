import logging

from datetime import datetime
from datetime import timedelta
from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import channel
from google.appengine.ext import db

from models.db.session import Session

class NotificationHandler(webapp.RequestHandler):
	def post(self):
		self.station_key = db.Key(self.request.get("station_key"))
		self.json = self.request.get("data")
		self.excluded_channel_id = self.request.get("excluded_channel_id")

		# Get active sessions
		q = Session.all()
		q.filter("station", self.station_key)
		q.filter("ended", None)
		q.filter("created >", datetime.now() - timedelta(0,7200))
		
		# For the moment we will only fetch the 100 listening sessions
		active_sessions = q.fetch(100)
		
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