from controllers.base import *

from django.utils import simplejson

from models.db.station import Station
from models.db.contribution import Contribution
from models.db.track import Track
from models.interface.station import InterfaceStation
from models.notifiers.track import TrackNotifier

from google.appengine.api import channel

class AddTrackHandler(BaseHandler):
	@login_required
	def post(self):
		self.station_key = self.request.get("station_key")
		self.channel_id = self.request.get("channel_id")
		
		tracks_to_add = simplejson.loads(self.request.get("tracks"))
		station_proxy = InterfaceStation(station_key = self.station_key)
		tracks_added = station_proxy.add_tracks(tracks_to_add, str(self.current_user.key()))
			
		if(tracks_added):
			# Send message to everyone 
			notifier = TrackNotifier(self.station_key, tracks_added, self.channel_id)
			logging.info("Everybody notified")
			# Send response
			self.response.out.write(simplejson.dumps({"status":"Added"}))
		else:
			# Send response
			self.response.out.write(simplejson.dumps({"status":"notAdded"}))


application = webapp.WSGIApplication([
	(r"/track/add", AddTrackHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()