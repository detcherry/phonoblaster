import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.track import Track

class Favorite(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "favoriteTrack")
	user = db.ReferenceProperty(User, required = True, collection_name = "favoriteUser")
	created = db.DateTimeProperty(auto_now_add = True)
	
	@staticmethod
	def get_extended_favorites(favorites):
		extended_favorites = []
		
		if(favorites):
			track_keys = []
			for f in favorites:
				track_key = Favorite.track.get_value_for_datastore(f)
				track_keys.append(track_key)
		
			tracks = db.get(track_keys)
			logging.info("Tracks retrieved from datastore")
			
			extended_tracks = Track.get_extended_tracks(tracks)
			logging.info("Extended tracks generated from datastore")
			
			station_keys = []
			for t in tracks:
				station_key = Track.station.get_value_for_datastore(t)
				station_keys.append(station_key)
			stations = db.get(station_keys)
			logging.info("Stations retrieved from datastore")
			
			for favorite, extended_track, station in zip(favorites, extended_tracks, stations):
				extended_favorite = Favorite.get_extended_favorite(favorite, extended_track, station)
				extended_favorites.append(extended_favorite)
		
		logging.info("Extended favorites generated")
		return extended_favorites
		
	@staticmethod
	def get_extended_favorite(favorite, extended_track, station):
		extended_favorite = {
			"type": "favorite",
			"created":  timegm(favorite.created.utctimetuple()),
			"youtube_id": extended_track["youtube_id"],
			"youtube_title": extended_track["youtube_title"],
			"youtube_duration": extended_track["youtube_duration"],
			"track_id": extended_track["track_id"],
			"track_created": extended_track["track_created"],
			"track_admin": extended_track["track_admin"],
			"track_submitter_key_name": station.key().name(),
			"track_submitter_name": station.name,
			"track_submitter_url": "/" + station.shortname,
		}
		
		return extended_favorite
		
		
		
		
			
			