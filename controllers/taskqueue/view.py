import logging

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.db.track import Track
from models.db.view import View
from models.db.air import Air
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
			youtube_id = live_broadcast["youtube_id"]
			youtube_duration = int(live_broadcast["youtube_duration"])
			youtube_title = live_broadcast["youtube_title"]
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
			user_extended_sessions = []
			for e in extended_sessions:
				if e["listener_key_name"] is not None:
					user_extended_sessions.append(db.Key.from_path("User", e["listener_key_name"]))
			
			user_keys = list(set(user_extended_sessions))
			
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
			
			air = Air(
				key_name = station_proxy.station.key().name(),
				shortname = station_proxy.station.shortname,
				name = station_proxy.station.name,
				link = station_proxy.station.link,
				youtube_id = youtube_id,
				youtube_duration = youtube_duration,
				youtube_title = youtube_title,
				expired = datetime.utcfromtimestamp(int(live_broadcast["expired"]))
			)
			air.put()
			logging.info("Air story put in datastore")
			
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