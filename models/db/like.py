import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.station import Station
from models.db.track import Track

class Like(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "likeTrack")
	listener = db.ReferenceProperty(Station, required = True, collection_name = "likeListener")
	created = db.DateTimeProperty(auto_now_add = True)
	
	@staticmethod
	def get_extended_likes(likes):
		extended_likes = []
		
		if(likes):
			track_keys = []
			for l in likes:
				track_key = Like.track.get_value_for_datastore(l)
				track_keys.append(track_key)
		
			tracks = db.get(track_keys)
			logging.info("Tracks retrieved from datastore")
			
			station_keys = []
			for t in tracks:
				station_key = Track.station.get_value_for_datastore(t)
				station_keys.append(station_key)
			stations = db.get(station_keys)
			logging.info("Stations retrieved from datastore")
			
			for like, track, station in zip(likes, tracks, stations):
				extended_like = Like.get_extended_like(like, track, station)
				extended_likes.append(extended_like)
		
		logging.info("Extended likes generated")
		return extended_likes
	
	@staticmethod
	def get_extended_like(like, track, station):
		extended_like = {
			"created":  timegm(like.created.utctimetuple()),
			"youtube_id": track.youtube_id,
			"youtube_title": track.youtube_title,
			"youtube_duration": track.youtube_duration,
			"track_id": str(track.key().id()),
			"track_created": timegm(track.created.utctimetuple()),
			"track_submitter_key_name": station.key().name(),
			"track_submitter_name": station.name,
			"track_submitter_url": "/" + station.shortname,
		}
		
		return extended_like