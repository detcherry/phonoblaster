from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api import channel

from models.db.session import Session

class MessageNotifier():
	
	def __init__(self, station, message, excluded_channel_id):
		self.station = station
		self.message = message
		self.excluded_channel_id = excluded_channel_id
		self.build()
		self.send()
	
	def build(self):
		if(self.message):
			self.output = {
				"type": "chat_new",
				"content" : {
					"text": self.message.text,
					"author_id": self.message.author.key().id(),
					"author_public_name": self.message.author.public_name,
					"author_fcbk_id": self.message.author.facebook_id,
					"added": timegm(self.message.added.utctimetuple()),
				}
			}

	def send(self):
		q = Session.all()
		q.filter("station", self.station.key())
		q.filter("ended", None)
		active_sessions = q.filter("created >", datetime.now() - timedelta(0,7200))
		#active_sessions = Session.all().filter("station", self.station.key()).filter("ended", None)

		for session in active_sessions:
			if(session.channel_id != self.excluded_channel_id):
				channel.send_message(session.channel_id, simplejson.dumps(self.output))
	