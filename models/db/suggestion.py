import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.track import Track
from models.db.station import Station
from models.db.user import User

class Suggestion(db.Model):
	"""
		message (optional)- message added by the user with the suggestion
		youtube_id - ID of the track on Youtube
		station - recipient of the suggestion
		user - suggestion submitter	
	"""
	
	message = db.StringProperty(required = False)
	youtube_id = db.StringProperty(required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "suggestionStation")
	user = db.ReferenceProperty(User, required = True, collection_name = "suggestionUser")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_extended_suggestions(suggestions):
		extended_suggestions = []
		
		if(suggestions):
			youtube_ids = []
			user_keys = []

			for s in suggestions:
				youtube_ids.append(s.youtube_id)
				
				user_key = Suggestion.user.get_value_for_datastore(s)
				user_keys.append(user_key)
			
			youtube_tracks = Youtube.get_extended_tracks(youtube_ids)
			logging.info("Youtube tracks retrieved")
			
			users = db.get(user_keys)
			logging.info("Users retrieved from datastore")
				
			for suggestion, youtube_track, user in zip(suggestions, youtube_tracks, users):
				# Check if the Youtube track exists
				if(youtube_track):
					extended_suggestion = Suggestion.get_extended_suggestion(suggestion, youtube_track, user)
					extended_suggestions.append(extended_suggestion)

		logging.info("Extended suggestions generated")
		return extended_suggestions

	@staticmethod
	def get_extended_suggestion(suggestion, youtube_track, user):	
		extended_suggestion = {
			"key_name": suggestion.key().name(),
			"message": suggestion.message,
			"type": "suggestion",
			"created": timegm(suggestion.created.utctimetuple()),
			"youtube_id": youtube_track["id"],
			"youtube_title": youtube_track["title"],
			"youtube_duration": youtube_track["duration"],
			"track_submitter_key_name": user.key().name(),
			"track_submitter_name": user.first_name + " " + user.last_name,
			"track_submitter_url": "/user/" + user.key().name(),
		}

		return extended_suggestion
