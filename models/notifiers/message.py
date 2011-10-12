from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api.labs.taskqueue import Task

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
		task = Task(
			url = "/taskqueue/notify",
			params = { 
				"station_key": str(self.station.key()),
				"data": simplejson.dumps(self.data),
				"excluded_channel_id": self.excluded_channel_id,
			},
		)
		task.add(
			queue_name = "message-queue-1"
		)
	