import logging
from datetime import datetime
from datetime import timedelta
import django_setup
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi
from models.db.suggestion import Suggestion
from models.db.youtube import Youtube

class ApiSuggestionsHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station
		
		if(station):
			q = Suggestion.all()
			q.filter("station", station.key())
			q.order("-created")
			suggestions = q.fetch(20) # Arbitrary number
		
			extended_suggestions = Suggestion.get_extended_suggestions(suggestions)
			self.response.out.write(json.dumps(extended_suggestions))
		else:
			self.error(404)
	
	@login_required
	def post(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station
		user = self.user_proxy.user
		admin = self.user_proxy.is_admin_of(station.key().name())

		suggestion_json = json.loads(self.request.get("content"))

		if(suggestion_json and not admin):
			track = None
			extended_track = None

			# Check when the user submitted his last suggestion
			q = Suggestion.all()
			q.filter("user", user)
			q.filter("station", station)
			q.filter("created >", datetime.utcnow() - timedelta(0,30))
			user_last_suggestion = q.get()

			if(user_last_suggestion):
				extended_suggestion = None
				logging.info("User submitted a suggestion shortly")
			else:
				logging.info("User did not submit a suggestion shortly")
				suggestion = Suggestion(
					key_name = suggestion_json["key_name"],
					message = suggestion_json["message"][:140].replace("\n"," "),
					youtube_id = suggestion_json["youtube_id"],
					youtube_title = suggestion_json["youtube_title"],
					youtube_duration = suggestion_json["youtube_duration"],
					station = station.key(),
					user = user.key(),
				)
	
				suggestion.put()
				logging.info("New suggestion saved into the datastore")
	
				extended_suggestion = Suggestion.get_extended_suggestion(suggestion, user)
				
				# Increment the user number of suggestions
				station_proxy.increment_suggestions_counter()
		
		response = False
		if(extended_suggestion):
			# Add a taskqueue to warn everyone
			suggestion_data = {
				"entity": "suggestion",
				"event": "new",
				"content": extended_suggestion,
			}

			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(suggestion_data)
				}
			)
			task.add(queue_name="suggestions-queue")
			response = True

		self.response.out.write(json.dumps({ "response": response }))

