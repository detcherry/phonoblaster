import logging
from random import randrange

from controllers.cron import config

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.interface.station import InterfaceStation
from models.notifiers.track import TrackNotifier

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
		"""
		
		# Init the keys
		welloiled_key = db.Key.from_path("Station", config.WELLOILED_ID)
		darlingvibes_key = db.Key.from_path("Station", config.DARLINGVIBES_ID)
		
		# Init the proxys
		welloiled_proxy = InterfaceStation(station_key = welloiled_key)
		darlingvibes_proxy = InterfaceStation(station_key = darlingvibes_key)
		
		# Init the creators
		welloiled_creator = welloiled_proxy.station_creator
		darlingvibes_creator = darlingvibes_proxy.station_creator
		
		# Determine how much room is left in each station tracklist
		room_in_welloiled = 10 - len(welloiled_proxy.station_tracklist)
		room_in_darlingvibes = 10 - len(darlingvibes_proxy.station_tracklist)
		
		# Init the collections
		welloiled_collection = config.WELLOILED_LIBRARY
		darlingvibes_collection = config.DARLINGVIBES_LIBRARY
		welloiled_collection_length = len(welloiled_collection)
		darlingvibes_collection_length = len(darlingvibes_collection)
		
		# Collect tracks to add in welloiled and darlingvibes (only collect as many as necessary)
		welloiled_tracks_to_add = []
		for i in range(room_in_welloiled):
			random_integer = randrange(welloiled_collection_length)
			random_track = welloiled_collection[random_integer]
			welloiled_tracks_to_add.append(random_track)
		
		darlingvibes_tracks_to_add = []
		for i in range(room_in_darlingvibes):
			random_integer = randrange(darlingvibes_collection_length)
			random_track = darlingvibes_collection[random_integer]
			darlingvibes_tracks_to_add.append(random_track)
		
		# Add tracks 
		welloiled_tracks_added = welloiled_proxy.add_tracks(welloiled_tracks_to_add, welloiled_creator.key())
		darlingvibes_tracks_added = darlingvibes_proxy.add_tracks(darlingvibes_tracks_to_add, darlingvibes_creator.key())
		
		# Notify everybody
		welloiled_notifier = TrackNotifier(welloiled_key, welloiled_tracks_added, None)
		darlingvibes_notifier = TrackNotifier(darlingvibes_key, darlingvibes_tracks_added, None)


application = webapp.WSGIApplication([
	(r"/cron/fake", FakeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()


