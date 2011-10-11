from controllers.station.root import *

from django.utils import simplejson

from models.queue import Queue
from models.notifiers.track import TrackNotifier

from google.appengine.api import channel


class StationShuffleHandler(RootStationHandler):
	@login_required
	def post(self):
		self.station_key = self.request.get("station_key")
		self.current_station = Station.get(self.station_key)
		self.queue = Queue(self.station_key)
		self.channel_id = self.request.get("channel_id")
		
		if(self.allowed_to_post):
			tracks_added = self.queue.shuffle(self.current_user.key())
			if(tracks_added):				
				# Send message to everyone
				notifier = TrackNotifier(self.current_station, tracks_added, self.channel_id)
				
				last_track_added = tracks_added[-1]
				#Say expiration time for the station is expiration of this latest track
				self.current_station.active = last_track_added.expired
				self.current_station.put()
				
				jsonResponse = {"status": "shuffled"}
			else:
				jsonResponse = {"status": "not_shuffled"}
			self.response.out.write(simplejson.dumps(jsonResponse))
		else:
			self.error(403)


application = webapp.WSGIApplication([
	(r"/station/shuffle", StationShuffleHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()