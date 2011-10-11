from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api import channel
from google.appengine.api.labs.taskqueue import Task

from models.db.track import Track
from models.db.user import User
#from models.notifiers.notifier import Notifier

class TrackNotifier():
	
	def __init__(self, station, tracklist, excluded_channel_id):
		self.station = station
		self.tracklist = tracklist
		self.excluded_channel_id = excluded_channel_id
		self.build()
		self.sendToMe()
		self.sendToEveryone()
	
	def build(self):
		self.output = []
		for track in self.tracklist:
			self.output.append({
				"phonoblaster_id": str(track.key().id()),
				"title":track.youtube_title,
				"id": track.youtube_id,
				"thumbnail": track.youtube_thumbnail_url,
				"duration": track.youtube_duration,
				"submitter_id": track.submitter.key().id(),
				"submitter_fcbk_id": track.submitter.facebook_id,
				"added": timegm(track.added.utctimetuple()),
				"expired": timegm(track.expired.utctimetuple()),
			})
		self.data = {
			"type": "tracklist_new",
			"content": self.output,
		}
	
	def sendToMe(self):
		channel.send_message(self.excluded_channel_id, simplejson.dumps(self.data))
	
	def sendToEveryone(self):
		#notifier = Notifier(self.station.key(), self.data, self.excluded_channel_id)
		#notifier.send()
		task = Task(
			url = "/taskqueue/track",
			params = { 
				"station_key": str(self.station.key()),
				"data": simplejson.dumps(self.data),
				"excluded_channel_id": self.excluded_channel_id,
			},
		)
		task.add(
			queue_name = "tracklist-queue"
		)
	
