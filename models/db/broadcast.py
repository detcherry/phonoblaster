import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.station import Station
from models.db.track import Track

class Broadcast(db.Model):
	"""
		track - track being broadcast
		station - where the track is being broadcast
		submitter (optional) - if the broadcast has been suggested by a submitter (e.g. a listener)
	"""
	
	track = db.ReferenceProperty(Track, required = True, collection_name = "broadcastTrack")
	station = db.ReferenceProperty(Station, required = True, collection_name = "broadcastStation")
	submitter = db.ReferenceProperty(Station, required = False, collection_name = "broadcastSubmitter")
	youtube_id = db.StringProperty(required = False)
	youtube_title = db.StringProperty(required = False)
	youtube_duration = db.IntegerProperty(required = False)
	soundcloud_id = db.StringProperty(required = False)
	soundcloud_title = db.StringProperty(required = False)
	soundcloud_duration = db.IntegerProperty(required = False)
	soundcloud_thumbnail = db.StringProperty(required = False)
	created = db.DateTimeProperty(auto_now_add = True)
	
	@staticmethod
	def get_extended_broadcasts(broadcasts, host):
		extended_broadcasts = []
		ordered_extended_broadcasts = []
		
		if(broadcasts):
			# Differentiate regular broadcast from rebroadcasts
			regular_broadcasts = []
			regular_broadcasts_submitters = []

			rebroadcasts = []
			rebroadcasts_submitter_keys = []
			rebroadcasts_submitters = []

			for i in xrange(0,len(broadcasts)):
				b = broadcasts[i]
				if b.submitter is not None:
					rebroadcasts_submitter_keys.append(Broadcast.submitter.get_value_for_datastore(b))
					rebroadcasts.append(b)
				else:
					regular_broadcasts_submitters.append(host)
					regular_broadcasts.append(b)
			
			rebroadcasts_submitters = db.get(rebroadcasts_submitter_keys)
			
			submitters = regular_broadcasts_submitters + rebroadcasts_submitters
			unordered_broadcasts = regular_broadcasts + rebroadcasts
			
			for broadcast, submitter in zip(unordered_broadcasts, submitters):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, submitter)
				extended_broadcasts.append(extended_broadcast)
			
			# Order the broadcasts that have been built from different sources (same order as the Datastore entities)
			for b in broadcasts:
				key_name = b.key().name()
				for e in extended_broadcasts:
					if(e["key_name"] == key_name):
						ordered_extended_broadcasts.append(e)
						break

		return ordered_extended_broadcasts
		
	@staticmethod
	def get_extended_broadcast(broadcast, submitter):
		extended_broadcast = {
			"key_name": broadcast.key().name(),
			"created": timegm(broadcast.created.utctimetuple()),
			"track_id": Broadcast.track.get_value_for_datastore(broadcast).id(),
			"track_submitter_key_name": submitter.key().name(),
			"track_submitter_name": submitter.name,
			"track_submitter_url": submitter.shortname
		}
		
		if(broadcast.youtube_id):
			extended_broadcast.update({
				"type": "youtube",
				"id": broadcast.youtube_id,
				"title": broadcast.youtube_title,
				"duration": broadcast.youtube_duration,
				"thumbnail": "https://i.ytimg.com/vi/" + broadcast.youtube_id + "/default.jpg",
			})
		else:
			extended_broadcast.update({
				"type" : "soundcloud",
				"id": broadcast.soundcloud_id,
				"title": broadcast.soundcloud_title,
				"duration": broadcast.soundcloud_duration,
				"thumbnail": broadcast.soundcloud_thumbnail,
			})
		
		return extended_broadcast
