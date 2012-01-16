import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station
from models.db.track import Track

class Broadcast(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "broadcastTrack")
	station = db.ReferenceProperty(Station, required = True, collection_name = "broadcastStation")
	expired = db.DateTimeProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	
	@staticmethod
	def get_extended_broadcasts(broadcasts, current_station):
		extended_broadcasts = []
		
		if(broadcasts):
			track_keys = []
			for b in broadcasts:
				track_key = Broadcast.track.get_value_for_datastore(b)
				track_keys.append(track_key)
				
			tracks = db.get(track_keys)
			logging.info("Tracks retrieved from datastore")
			extended_tracks = Track.get_extended_tracks(tracks)
			logging.info("Extended tracks generated from Youtube")
	
			regular_broadcasts = []
			regular_tracks = []
			regular_extended_tracks = []

			suggested_broadcasts = []
			suggested_tracks = []
			suggested_extended_tracks = []
			user_keys = []
	
			favorited_broadcasts = []
			favorited_tracks = []
			favorited_extended_tracks = []
			station_keys = []
	
			for broadcast, track, extended_track in zip(broadcasts, tracks, extended_tracks):
				station_key = Track.station.get_value_for_datastore(track)
				
				# We check if the track is really on Youtube
				if(extended_track):
					if(station_key == current_station.key()):
						if(track.admin):
							regular_broadcasts.append(broadcast)
							regular_tracks.append(track)
							regular_extended_tracks.append(extended_track)
						else:
							suggested_broadcasts.append(broadcast)
							suggested_tracks.append(track)
							suggested_extended_tracks.append(extended_track)
							user_key = Track.user.get_value_for_datastore(track)
							user_keys.append(user_key)					
					else:
						favorited_broadcasts.append(broadcast)
						favorited_tracks.append(track)
						favorited_extended_tracks.append(extended_track)
						station_keys.append(station_key)
			
			# First let's format the regular broadcasts
			for broadcast, extended_track in zip(regular_broadcasts, regular_extended_tracks):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, extended_track, current_station, None)
				extended_broadcasts.append(extended_broadcast)
			
			# Then retrieve users and format suggested broadcasts
			users = db.get(user_keys)
			for broadcast, extended_track, user in zip(suggested_broadcasts, suggested_extended_tracks, users):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, extended_track, current_station, user)
				extended_broadcasts.append(extended_broadcast)
			
			# Finally retrieve stations and format broadcasts from tracks favorited somewhere else
			stations = db.get(station_keys)
			for broadcast, extended_track, station in zip(favorited_broadcasts, favorited_extended_tracks, stations):
				extended_broadcast = Broadcast.get_extended_broadcast(broadcast, extended_track, station, None)
				extended_broadcasts.append(extended_broadcast)
		
		return extended_broadcasts

	@staticmethod
	def get_extended_broadcast(broadcast, extended_track, station, user):
		extended_broadcast = None
				
		extended_broadcast = {
			"key_name": broadcast.key().name(),
			"created": timegm(broadcast.created.utctimetuple()),
			"expired": timegm(broadcast.expired.utctimetuple()),	
			"youtube_id": extended_track["youtube_id"],
			"youtube_title": extended_track["youtube_title"],
			"youtube_duration": extended_track["youtube_duration"],
			"track_id": extended_track["track_id"],
			"track_created": extended_track["track_created"],
			"track_admin": extended_track["track_admin"],
		}
		
		broadcast_station_key = Broadcast.station.get_value_for_datastore(broadcast)
		if(broadcast_station_key == station.key()):
			# It's a regular broadcast
			if(extended_track["track_admin"]):
				extended_broadcast["track_submitter_key_name"] = station.key().name()
				extended_broadcast["track_submitter_name"] = station.name
				extended_broadcast["track_submitter_url"] = "/" + station.shortname
				extended_broadcast["type"] = "track"
			# It's a suggested broadcast
			else:
				extended_broadcast["track_submitter_key_name"] = user.key().name()
				extended_broadcast["track_submitter_name"] = user.first_name + " " + user.last_name
				extended_broadcast["track_submitter_url"] = "/user/" + user.key().name()
				extended_broadcast["type"] = "suggestion"
		# It's a rebroadcast	
		else:
			extended_broadcast["track_submitter_key_name"] = station.key().name()
			extended_broadcast["track_submitter_name"] = station.name
			extended_broadcast["track_submitter_url"] = "/" + station.shortname
			extended_broadcast["type"] = "favorite"

		return extended_broadcast
				
		
		
		