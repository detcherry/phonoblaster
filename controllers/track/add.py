from controllers.base import *

from calendar import timegm
from django.utils import simplejson

from models.db.station import Station
from models.db.contribution import Contribution
from models.db.track import Track
from models.queue import Queue
from models.notifiers.track import TrackNotifier

class AddTrackHandler(BaseHandler):
	@login_required
	def post(self):
		self.youtube_title = self.request.get("title")
		self.youtube_id = self.request.get("id")
		self.youtube_thumbnail = self.request.get("thumbnail")
		self.youtube_duration = self.request.get("duration")
		self.station_key = self.request.get("station_key")
				
		self.station = Station.get(self.station_key)
		
		if(self.isAllowedToAdd()):
			track_added = []
			track_added.append(self.addTrack())
			
			if(track_added):
				#Send message to everyone 
				notifier = TrackNotifier(self.station, track_added, "tracklist_new")
				
				#Say expiration time for the station is expiration of this latest track
				self.station.active = track_added[0].expired
				self.station.put()
				
				self.response.out.write(simplejson.dumps({
					"status":"Added"
				}))
				
			else:
				self.response.out.write(simplejson.dumps({
					"status":"notAdded"
				}))
		else:
			self.error(403)
	
	def isAllowedToAdd(self):
		#If current user is the creator of the station
		if(self.current_user.key() == self.station.creator.key()):
			return True
		else:
			contribution = Contribution.all().filter("station", self.station.key()).filter("contributor", self.current_user.key()).get()
			if(contribution):
				return True
			
			return False
	
	def addTrack(self):
		queue = Queue(self.station_key)
		track = queue.addTrack(self.youtube_title, self.youtube_id, self.youtube_thumbnail, self.youtube_duration, self.current_user.key())
		return track

application = webapp.WSGIApplication([
	(r"/track/add", AddTrackHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()