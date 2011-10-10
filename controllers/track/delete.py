from datetime import datetime
from datetime import timedelta

from controllers.base import *

from django.utils import simplejson

from models.db.station import Station
from models.db.track import Track
from models.db.session import Session
from models.queue import Queue

from models.notifiers.notifier import Notifier

class DeleteTrackHandler(BaseHandler):
	@login_required
	def post(self):
		phonoblaster_id = self.request.get("id")
		track_to_delete = Track.get_by_id(int(phonoblaster_id))
		
		if(self.current_user.key() == track_to_delete.submitter.key()):
			duration = timedelta(0,track_to_delete.youtube_duration)
			
			station_key = track_to_delete.station.key()
			queue = Queue(station_key)
			response = queue.deleteTrack(track_to_delete.key())
			
			if(response):
				# If the tracks has been removed, the station expiration time should be earlier (duration of the track removed)
				# PS: refactoring possible we have already fetch the track entity in the queue model
				station = Station.get(station_key)
				station.active -= duration
				station.put() 
				
				# Build the data
				self.data = {
					"type":"tracklist_delete",
					"content": phonoblaster_id,
				}
				# Send a message to everybody
				notifier = Notifier(station_key, self.data, None)
				notifier.send()
				
				self.response.out.write(simplejson.dumps({"status":"Added"}))
			else:
				self.response.out.write(simplejson.dumps({"status":"notAdded"}))
		else:
			self.error(403)

application = webapp.WSGIApplication([
	(r"/track/delete", DeleteTrackHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()