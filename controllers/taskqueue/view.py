import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.db.track import Track
from models.db.view import View
from models.api.station import StationApi
from google.appengine.api.taskqueue import Task

class ViewHandler(webapp.RequestHandler):
	def post(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		queue = station_proxy.queue
		
		if(queue):
			logging.info("Station on air")
			
			live_broadcast = queue[0]
			track_id = int(live_broadcast["track_id"])
			track_key = db.Key.from_path("Track", track_id)
			
			number_of_sessions = max(0,station_proxy.number_of_sessions)
			if(number_of_sessions):
				# Increase the station views counter
				station_proxy.increase_views_counter(number_of_sessions)
				logging.info("Station views counter increased")
			
				# Increase the track views counter
				Track.increase_views_counter(track_id, number_of_sessions)
				logging.info("Track views counter increased")
			
			extended_sessions = station_proxy.sessions
			user_keys = list(set([db.Key.from_path("User", e["listener_key_name"]) for e in extended_sessions]))
			
			views = []
			for user_key in user_keys:
				view = View(
					key_name = str(track_key.id()) + "." + str(user_key.name()),
					track = track_key,
					user = user_key,
				)
				views.append(view)
			
			db.put(views)
			logging.info("Views put in the datastore")
			
			# Start another task after this track has ended
			countdown = int(live_broadcast["youtube_duration"])
			
			task = Task(
				url = "/taskqueue/view",
				params = {
					"shortname": shortname,
				},
				countdown = countdown,
			)
			task.add(queue_name = "worker-queue")
			logging.info("Task view put in the queue")
		
		else:
			logging.info("Station off air")
		

		
application = webapp.WSGIApplication([
	(r"/taskqueue/view", ViewHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()