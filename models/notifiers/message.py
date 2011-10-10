from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api import channel

from models.notifiers.notifier import Notifier

class MessageNotifier():
	
	def __init__(self, station, message, excluded_channel_id):
		self.station = station
		self.message = message
		self.excluded_channel_id = excluded_channel_id
		self.build()
		self.send()
	
	def build(self):
		if(self.message):
			self.data = {
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
		notifier = Notifier(self.station.key(), self.data, self.excluded_channel_id)
		notifier.send()
	