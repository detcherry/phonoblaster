import logging
from random import randrange
from django.utils import simplejson

from controllers.cron import config

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.db.session import Session
from models.interface.station import InterfaceStation
from models.notifiers.track import TrackNotifier
from google.appengine.api.taskqueue import Task

class FakeHandler(webapp.RequestHandler):
	def get(self):
		"""
			This cron jobs aimed at faking 2 radio stations: welloiled & darlingvibes
			What we have to do every 30 minutes:
			- Init station proxy welloiled & darlingvibes
			- Determine how many tracks we can add
			- Picked a random number of tracks from the selection
			- Add them
			- Notify everybody listening
			- End/restart fake sessions for the creators
		"""
				
		# Init information
		welloiled = config.WELLOILED
		darlingvibes = config.DARLINGVIBES
		
		infos = [welloiled, darlingvibes]
		
		for info in infos:
			# Init the key
			key = db.Key.from_path("Station", info["id"])
		
			# Init the proxy
			proxy = InterfaceStation(station_key = key)
			
			# Init the creator
			creator = proxy.station_creator
			
			# Determine how much room is left in each station tracklist
			room = 10 - len(proxy.station_tracklist)
			
			# Init the library
			library = info["library"]
			library_length = len(library)
			
			# Collect tracks to add (only collect as many as necessary)
			tracks_to_add = []
			for i in range(room):
				random_integer = randrange(library_length)
				random_track = library[random_integer]
				tracks_to_add.append(random_track)
			
			# Add tracks
			tracks_added = proxy.add_tracks(tracks_to_add, creator.key())
			
			# Notify everybody
			notifier = TrackNotifier(key, tracks_added, None)
			
			# Get the creator session
			session_to_end = Session.all().filter("user", creator.key()).get()
			
			if(session_to_end):
				proxy.end_session(session_to_end)
			
				# Warn everybody
				listener_delete_output = {
					"session_id": session_to_end.key().id(),
				}
				listener_delete_data = {
					"type": "listener_delete",
					"content": listener_delete_output,
				}

				excluded_channel_id = None
				task = Task(
					url = "/taskqueue/notify",
					params = { 
						"station_key": str(key),
						"data": simplejson.dumps(listener_delete_data),
						"excluded_channel_id": excluded_channel_id,
					},
				)
				task.add(
					queue_name = "listener-queue-1"
				)
			
			# Restart a session
			new_session = proxy.add_session(user_key = creator.key())
			
			# Confirm the session
			proxy.confirm_session(new_session)
			
			# Inform everyone 
			new_listener = new_session.user
			listener_new_output = {
				"session_id": new_session.key().id(),
				"phonoblaster_id" : new_listener.key().id(),
				"public_name": new_listener.public_name,
				"facebook_id": new_listener.facebook_id,
			}
			listener_new_data = {
				"type":"listener_new",
				"content": listener_new_output,
			}

			excluded_channel_id = None
			task = Task(
				url = "/taskqueue/notify",
				params = { 
					"station_key": str(key),
					"data": simplejson.dumps(listener_new_data),
					"excluded_channel_id": excluded_channel_id,
				},
			)
			task.add(
				queue_name = "listener-queue-1"
			)


application = webapp.WSGIApplication([
	(r"/cron/fake", FakeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()


