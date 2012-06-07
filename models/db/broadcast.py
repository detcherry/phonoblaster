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
	submitter = db.ReferenceProperty(User, required = False, collection_name = "broadcastSubmitter")
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
	
			regular_broadcasts = []
			regular_tracks = []

			suggested_broadcasts = []
			suggested_tracks = []
			suggestions_submitter_keys = []
	
			favorited_broadcasts = []
			favorited_tracks = []
			favorite_submitter_keys = []
	
			for broadcast, track in zip(broadcasts, tracks):
				suggestions_submitter_key = Broadcast.user.get_value_for_datastore(broadcast)
				
				# Broadcast suggested by a user
				if(suggestions_submitter_key):
					suggested_broadcasts.append(broadcast)
					suggested_tracks.append(track)
					
					suggestions_submitter_keys.append(suggestions_submitter_key)
				else:
					favorited_submitter_key = Track.station.get_value_for_datastore(track)
					
					# Regular broadcast
					if(favorite_submitter_keys == host.key()):
						regular_broadcasts.append(broadcast)
						regular_tracks.append(track)
					# Rebroadcast from another station
					else:
						favorited_broadcasts.append(broadcast)
						favorited_tracks.append(track)

						favorite_submitter_keys.append(station_key)

			# First let's format the regular broadcasts
			for broadcast, track in zip(regular_broadcasts, regular_tracks):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, host, None)
				extended_broadcasts.append(extended_broadcast)

			# Then retrieve users and format suggested broadcasts
			submitters = db.get(suggestions_submitter_keys)
			for broadcast, track, submitter in zip(suggested_broadcasts, suggested_tracks, submitter):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, None, submitter)
				extended_broadcasts.append(extended_broadcast)

			# Finally retrieve stations and format broadcasts from tracks favorited somewhere else
			favorite_submitters = db.get(favorite_submitter_keys)
			for broadcast, track, favorite_submitter_keys in zip(favorited_broadcasts, favorited_tracks, favorite_submitters):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, favorite_submitter_key, None)
				extended_broadcasts.append(extended_broadcast)
			
			# Order the broadcasts that have been built from different sources (same order as the Datastore entities)
			for b in broadcasts:
				key_name = b.key().name()
				for e in extended_broadcasts:
					if(e["key_name"] == key_name):
						ordered_extended_broadcasts.append(e)
						break
			
		return ordered_extended_broadcasts	
	
	# TO BE CHANGED
	@staticmethod
	def get_extended_broadcast(broadcast, track, host,  submitter):
		extended_broadcast = None

		extended_broadcast = {
			"key_name": broadcast.key().name(),
			"created": timegm(broadcast.created.utctimetuple()),	
			"youtube_id": track.youtube_id,
			"youtube_title": track.youtube_title,
			"youtube_duration": track.youtube_duration,
			"track_id": track.key().id(),
			"track_created": timegm(track.created.utctimetuple()),
		}
		
		# It's a broadcast
		if(submitter):
			extended_broadcast["track_submitter_key_name"] = submitter.key().name()
			extended_broadcast["track_submitter_name"] = submitter.name
			extended_broadcast["track_submitter_url"] = "/" + submitter.shortname
			extended_broadcast["type"] = "rebrodcast"
		else:
			extended_broadcast["track_submitter_key_name"] = host.key().name()
			extended_broadcast["track_submitter_name"] = host.name
			extended_broadcast["track_submitter_url"] = "/" + host.shortname
			extended_broadcast["type"] = "track"
		
		return extended_broadcast
