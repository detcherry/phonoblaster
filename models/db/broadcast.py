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
	created = db.DateTimeProperty(auto_now_add = True)
	expired = db.DateTimeProperty()

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

			submitter_keys = []
			for i in xrange(0,len(broadcasts)):
				b = broadcasts[i]
				if b.submitter is not None:
					submitter_keys.append(b.submitter)
				else:
					submitter_keys.append(host.key())
					
			# Then retrieve submitters and format extended_broadcasts
			submitters = db.get(submitter_keys)
			logging.info("Submitters retrieved from datastore")

			for broadcast, track, submitter in zip(broadcasts, tracks, submitters):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, submitter)
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
