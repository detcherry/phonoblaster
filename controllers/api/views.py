import logging

from controllers.base import BaseHandler

from google.appengine.ext import db

from models.api.station import StationApi

from models.db.track import Track
from models.db.view import View

class ApiViewsHandler(BaseHandler):
	def post(self):
		shortname = self.request.get("shortname")		
		station_proxy = StationApi(shortname)
		
		queue = station_proxy.queue
		if(len(queue) > 0):
			# Increment the station views counter
			station_proxy.increment_views_counter()
			
			live_broadcast = queue[0]
			track_id = int(live_broadcast["track_id"])
			
			# Increment the views counter of the track which is live
			Track.increment_views_counter(track_id)
			
			# Store a view in the datastore
			if(self.user_proxy):
				track_key = db.Key.from_path("Track", track_id)
				user_key = self.user_proxy.user.key()
				
				q = View.all(keys_only = True)
				q.filter("track", track_key)
				q.filter("user", user_key)
				existing_view = q.get()
				
				if existing_view is None:
					new_view = View(
						track = track_key,
						user = user_key,
					)
					new_view.put()
					logging.info("New user view put in datastore")
				else:
					logging.info("User already viewed this track")
		