import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.track import Track
from models.db.station import Station

class Suggestion(db.Model):
	message = db.StringProperty(required=True)
	track = db.ReferenceProperty(Track, required = True, collection_name = "suggestionTrack")
	station = db.ReferenceProperty(Station, required = True, collection_name = "suggestionStation")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_extended_suggestions(suggestions):
		extended_suggestions = []
		
		if(suggestions):
			track_keys = []
			for s in suggestions:
				track_key = Suggestion.track.get_value_for_datastore(s)
				track_keys.append(track_key)
			
			tracks = db.get(track_keys)
			logging.info("Tracks retrieved from datastore")
			extended_tracks = Track.get_extended_tracks(tracks)
			logging.info("Extended tracks generated from datastore")
			
			user_keys = []
			for t in tracks:
				user_key = Track.user.get_value_for_datastore(t)
				user_keys.append(user_key)
			users = db.get(user_keys)
			logging.info("Users retrieved from datastore")
			
			for suggestion, extended_track, user in zip(suggestions, extended_tracks, users):
				# Check if the Youtube track exists
				if(extended_track):
					extended_suggestion = Suggestion.get_extended_suggestion(suggestion, extended_track, user)
					extended_suggestions.append(extended_suggestion)
		
		logging.info("Extended suggestions generated")
		return extended_suggestions
		
		
	@staticmethod
	def get_extended_suggestion(suggestion, extended_track, user):	
		extended_suggestion = {
			"key_name": suggestion.key().name(),
			"message": suggestion.message,
			"type": "suggestion",
			"created": timegm(suggestion.created.utctimetuple()),
			"youtube_id": extended_track["youtube_id"],
			"youtube_title": extended_track["youtube_title"],
			"youtube_duration": extended_track["youtube_duration"],
			"track_id": extended_track["track_id"],
			"track_created": extended_track["track_created"],
			"track_admin": extended_track["track_admin"],
			"track_submitter_key_name": user.key().name(),
			"track_submitter_name": user.first_name + " " + user.last_name,
			"track_submitter_url": "/user/" + user.key().name(),
		}
		
		return extended_suggestion
		
		
		
