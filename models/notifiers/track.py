from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api import channel

from models.db.track import Track
from models.db.user import User
from models.notifiers.notifier import Notifier

class TrackNotifier():
	
	def __init__(self, station, tracklist, method):
		self.station = station
		self.tracklist = tracklist
		self.method = method
		self.build()
		self.send()
	
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
			"type": self.method,
			"content": self.output,
		}
	
	def send(self):
		notifier = Notifier(self.station.key(), self.data, None)
		notifier.send()
