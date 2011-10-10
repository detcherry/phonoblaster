from datetime import datetime
from datetime import timedelta
from django.utils import simplejson

from google.appengine.api import channel

from models.db.session import Session

class Notifier():
	
	def __init__(self, station_key, data, excluded_channel_id = None):
		self.station_key = station_key
		self.json = simplejson.dumps(data)
		self.excluded_channel_id = excluded_channel_id
	
	def send(self):
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
		
		return active_sessions

		