import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station
from models.db.track import Track

class Broadcast(db.Model):
	"""
		track - track being broadcast
		station - where the track is being broadcast
		user (optional) - if the broadcast has been suggested by a user (e.g. a listener)
	"""
	
	track = db.ReferenceProperty(Track, required = True, collection_name = "broadcastTrack")
	station = db.ReferenceProperty(Station, required = True, collection_name = "broadcastStation")
	user = db.ReferenceProperty(User, required = False, collection_name = "broadcastUser")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_extended_broadcasts(broadcasts, current_station):
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
			user_keys = []
	
			favorited_broadcasts = []
			favorited_tracks = []
			station_keys = []
	
			for broadcast, track in zip(broadcasts, tracks):
				user_key = Broadcast.user.get_value_for_datastore(broadcast)
				
				# Broadcast suggested by a user
				if(user_key):
					suggested_broadcasts.append(broadcast)
					suggested_tracks.append(track)
					
					user_keys.append(user_key)
				else:
					station_key = Track.station.get_value_for_datastore(track)
					
					# Regular broadcast
					if(station_key == current_station.key()):
						regular_broadcasts.append(broadcast)
						regular_tracks.append(track)
					# Rebroadcast from another station
					else:
						favorited_broadcasts.append(broadcast)
						favorited_tracks.append(track)

						station_keys.append(station_key)

			# First let's format the regular broadcasts
			for broadcast, track in zip(regular_broadcasts, regular_tracks):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, current_station, None)
				extended_broadcasts.append(extended_broadcast)

			# Then retrieve users and format suggested broadcasts
			users = db.get(user_keys)
			for broadcast, track, user in zip(suggested_broadcasts, suggested_tracks, users):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, None, user)
				extended_broadcasts.append(extended_broadcast)

			# Finally retrieve stations and format broadcasts from tracks favorited somewhere else
			stations = db.get(station_keys)
			for broadcast, track, station in zip(favorited_broadcasts, favorited_tracks, stations):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, track, station, None)
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
	def get_extended_broadcast(broadcast, track, station, user):
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
		
		# It's a suggested broadcast
		if(user):
			extended_broadcast["track_submitter_key_name"] = user.key().name()
			extended_broadcast["track_submitter_name"] = user.first_name + " " + user.last_name
			extended_broadcast["track_submitter_url"] = "/user/" + user.key().name()
			extended_broadcast["type"] = "suggestion"
		else:
			extended_broadcast["track_submitter_key_name"] = station.key().name()
			extended_broadcast["track_submitter_name"] = station.name
			extended_broadcast["track_submitter_url"] = "/" + station.shortname

			broadcast_station_key = Broadcast.station.get_value_for_datastore(broadcast)
			# It's a regular broadcast
			if(broadcast_station_key == station.key()):
				extended_broadcast["type"] = "track"
			# It's a rebrodcast
			else:
				extended_broadcast["type"] = "favorite"
		
		return extended_broadcast
