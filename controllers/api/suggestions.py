import logging
from datetime import datetime
from datetime import timedelta
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi
from models.db.track import Track
from models.db.suggestion import Suggestion

class ApiSuggestionsHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station
		
		q = Suggestion.all()
		q.filter("station", station)
		q.order("created")
		suggestions = q.fetch(20) # Arbitrary number
		
		extended_suggestions = Suggestion.get_extended_suggestions(suggestions)
		self.response.out.write(json.dumps(extended_suggestions))
		
		
	@login_required
	def post(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station
		user = self.user_proxy.user
		admin = self.user_proxy.is_admin_of(station.key().name())
		
		suggestion = json.loads(self.request.get("content"))
		
		if(suggestion and not admin):
			track = None
			extended_track = None
			
			# Check when the user submitted his last suggestion
			q = Suggestion.all()
			q.filter("user", user)
			q.filter("station", station)
			q.filter("created >", datetime.utcnow() - timedelta(0,180))
			user_last_suggestion = q.get()
			
			if(user_last_suggestion):
				logging.info("User submitted a suggestion shortly")
			else:
				logging.info("User did not submit a suggestion shortly")
				if(suggestion["track_id"]):
					track = Track.get_by_id(int(suggestion["track_id"]))
					# If track on Phonoblaster, get extended track from Youtube
					if(track):
						extended_track = Track.get_extended_tracks([track])[0]
				else:
					# If obviously not, look for it though, save it otherwise and get extended track from Youtube
					if(suggestion["youtube_id"]):
						track, extended_track = Track.get_or_insert_by_youtube_id(suggestion["youtube_id"], station, user, admin)
		
				if(track and extended_track):
					suggestion = Suggestion(
						key_name = suggestion["key_name"],
						track = track.key(),
						station = station.key(),
						message = suggestion["message"][:140],
					)
			
					suggestion.put()
					logging.info("New suggestion saved into the datastore")
			
					extended_suggestion = Suggestion.get_extended_suggestion(suggestion, extended_track, user)
		
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
