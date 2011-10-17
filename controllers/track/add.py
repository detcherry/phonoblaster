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
		self.youtube_title = self.request.get("title")
		self.youtube_id = self.request.get("id")
		self.youtube_thumbnail = self.request.get("thumbnail")
		self.youtube_duration = self.request.get("duration")
		self.station_key = self.request.get("station_key")
		self.channel_id = self.request.get("channel_id")
		
		track_added = []
		station_proxy = InterfaceStation(station_key = self.station_key)
		track_added.append(
			station_proxy.add_track(self.youtube_title, self.youtube_id, self.youtube_thumbnail, self.youtube_duration, str(self.current_user.key()))
		)
		if(track_added):
			# Send message to everyone 
			notifier = TrackNotifier(self.station_key, track_added, self.channel_id)
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