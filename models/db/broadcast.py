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
	youtube_id = db.StringProperty()
	youtube_title = db.StringProperty()
	youtube_duration = db.IntegerProperty()
	created = db.DateTimeProperty(auto_now_add = True)
	
	"""
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
			"youtube_id": broadcast.youtube_id,
			"youtube_title": broadcast.youtube_title,
			"youtube_duration": broadcast.youtube_duration,
			"track_id": Broadcast.track.get_value_for_datastore(broadcast).id(),
			"track_submitter_key_name": submitter.key().name(),
			"track_submitter_name": submitter.name,
			"track_submitter_url": submitter.shortname
		}
		
		return extended_broadcast
	"""
	
	@staticmethod
	def get_extended_broadcasts(broadcasts, host):
		extended_broadcasts = []
		ordered_extended_broadcasts = []
		
		if(broadcasts):
			track_keys = []
			for b in broadcasts:
				track_key = Broadcast.track.get_value_for_datastore(b)
				track_keys.append(track_key)
				
			tracks = db.get(track_keys)
			logging.info("Tracks retrieved from datastore")

			# Differentiate regular broadcast from rebroadcasts
			regular_broadcasts = []
			rebroadcasts = []

			rebroadcasts_submitter_keys = []
			regular_broadcasts_submitter = []

			rebroadcasts_tracks = []
			regular_broadcasts_tracks = []

			for i in xrange(0,len(broadcasts)):
				b = broadcasts[i]
				if b.submitter is not None:
					rebroadcasts_submitter_keys.append(Broadcast.submitter.get_value_for_datastore(b))
					rebroadcasts_tracks.append(tracks[i])
					rebroadcasts.append(b)
				else:
					regular_broadcasts_submitter.append(host)
					regular_broadcasts_tracks.append(tracks[i])
					regular_broadcasts.append(b)
					
			# Then retrieve submitters and format extended_broadcasts
			rebroadcasts_submitter = db.get(rebroadcasts_submitter_keys)
			logging.info("Submitters retrieved from datastore")

			submitters = rebroadcasts_submitter + regular_broadcasts_submitter
			unordered_broadcasts = rebroadcasts + regular_broadcasts
			tracks = rebroadcasts_tracks + regular_broadcasts_tracks

			for broadcast, track, submitter in zip(unordered_broadcasts, tracks, submitters):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, submitter)
				extended_broadcasts.append(extended_broadcast)

			# Order the broadcasts that have been built from different sources (same order as the Datastore entities)
			ordered_extended_broadcasts = []

			for b in broadcasts:
				key_name = b.key().name()
				for e in extended_broadcasts:
					if(e["key_name"] == key_name):
						ordered_extended_broadcasts.append(e)
						break

		return ordered_extended_broadcasts

	@staticmethod
	def get_extended_broadcast(broadcast, track, submitter):
		extended_broadcast = None

		extended_broadcast = {
			"key_name": broadcast.key().name(),
			"created": timegm(broadcast.created.utctimetuple()),	
			"youtube_id": track.youtube_id,
			"youtube_title": track.youtube_title,
			"youtube_duration": track.youtube_duration,
			"track_id": track.key().id(),
			"track_created": timegm(track.created.utctimetuple()),
			"track_submitter_key_name": submitter.key().name(),
			"track_submitter_name": submitter.name,
			"track_submitter_url": submitter.shortname
		}
		
		return extended_broadcast