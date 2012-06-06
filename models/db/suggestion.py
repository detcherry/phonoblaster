import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.track import Track
from models.db.station import Station
from models.db.user import User
from models.db.youtube import Youtube

class Suggestion(db.Model):
	"""
		message (optional)- message added by the user with the suggestion
		youtube_id - ID of the track on Youtube
		youtube_title - String video title
		youtube_duration - Integer duration of the video in seconds
		youtube_music - Boolen, indicates if the video category is music or not
		station - recipient of the suggestion
		user - suggestion submitter	
	"""
	
	message = db.StringProperty(required = False)
	youtube_id = db.StringProperty(required = True)
	youtube_title = db.StringProperty()
	youtube_duration = db.IntegerProperty()
	station = db.ReferenceProperty(Station, required = True, collection_name = "suggestionStation")
	user = db.ReferenceProperty(User, required = True, collection_name = "suggestionUser")
	created = db.DateTimeProperty(auto_now_add = True)

	# TO BE CHANGED
	@staticmethod
	def get_extended_suggestions(suggestions):
		extended_suggestions = []
		
		if(suggestions):
			user_keys = []

			for s in suggestions:
				user_key = Suggestion.user.get_value_for_datastore(s)
				user_keys.append(user_key)
			
			users = db.get(user_keys)
			logging.info("Users retrieved from datastore")
				
			for suggestion, user in zip(suggestions, users):
				extended_suggestion = Suggestion.get_extended_suggestion(suggestion, user)
				extended_suggestions.append(extended_suggestion)

		logging.info("Extended suggestions generated")
		return extended_suggestions

	# TO BE CHANGED
	@staticmethod
	def get_extended_suggestion(suggestion, user):	
		extended_suggestion = {
			"key_name": suggestion.key().name(),
			"message": suggestion.message,
			"type": "suggestion",
			"created": timegm(suggestion.created.utctimetuple()),
			"youtube_id": suggestion.youtube_id,
			"youtube_title": suggestion.youtube_title,
			"youtube_duration": suggestion.youtube_duration,
			"track_submitter_key_name": user.key().name(),
			"track_submitter_name": user.first_name + " " + user.last_name,
			"track_submitter_url": "/user/" + user.key().name(),
		}

		return extended_suggestion
