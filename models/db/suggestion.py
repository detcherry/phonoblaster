import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.track import Track
from models.db.station import Station
from models.db.youtube import Youtube

class Suggestion(db.Model):
	"""
		message (optional)- message added by the user with the suggestion
		youtube_id - ID of the track on Youtube
		youtube_title - String video title
		youtube_duration - Integer duration of the video in seconds
		youtube_music - Boolen, indicates if the video category is music or not
		host - recipient of the suggestion
		submitter - suggestion submitter	
	"""
	
	message = db.StringProperty(required = False)
	youtube_id = db.StringProperty(required = True)
	youtube_title = db.StringProperty()
	youtube_duration = db.IntegerProperty()
	host = db.ReferenceProperty(Station, required = True, collection_name = "suggestionHost")
	submitter = db.ReferenceProperty(User, required = True, collection_name = "suggestionSubmitter")
	created = db.DateTimeProperty(auto_now_add = True)

	@staticmethod
	def get_extended_suggestions(suggestions):
		extended_suggestions = []
		
		if(suggestions):
			submitter_keys = []

			for s in suggestions:
				submitter_key = Suggestion.submitter.get_value_for_datastore(s)
				submitter_keys.append(submitter_key)
			
			submitters = db.get(submitter_keys)
			logging.info("Submitters retrieved from datastore")
				
			for suggestion, submitter in zip(suggestions, submitters):
				extended_suggestion = Suggestion.get_extended_suggestion(suggestion, submitter)
				extended_suggestions.append(extended_suggestion)

		logging.info("Extended suggestions generated")
		return extended_suggestions

	@staticmethod
	def get_extended_suggestion(suggestion, submitter):	
		extended_suggestion = {
			"key_name": suggestion.key().name(),
			"message": suggestion.message,
			"type": "rebroadcast",
			"created": timegm(suggestion.created.utctimetuple()),
			"youtube_id": suggestion.youtube_id,
			"youtube_title": suggestion.youtube_title,
			"youtube_duration": suggestion.youtube_duration,
			"track_submitter_key_name": submitter.key().name(),
			"track_submitter_name": submitter.name,
			"track_submitter_url": "/" + submitter.shortname,
		}

		return extended_suggestion
