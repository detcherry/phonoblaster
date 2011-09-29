from controllers.base import *

from django.utils import simplejson

from models.db.station import Station
from models.db.track import Track
from models.db.session import Session
from models.queue import Queue

from google.appengine.api import channel

class DeleteTrackHandler(BaseHandler):
	@login_required
	def post(self):
		phonoblaster_id = self.request.get("id")
		track_to_delete = Track.get_by_id(int(phonoblaster_id))
		
		if(self.current_user.key() == track_to_delete.submitter.key()):
			station_key = track_to_delete.station.key()
			queue = Queue(station_key)
			response = queue.deleteTrack(track_to_delete.key())
			
			if(response):
				self.data = {
					"type":"tracklist_delete",
					"content": phonoblaster_id,
				}
				active_sessions = Session.all().filter("station", station_key).filter("ended", None)
				for session in active_sessions:
					channel.send_message(session.channel_id, simplejson.dumps(self.data))
				
				self.response.out.write(simplejson.dumps({
					"status":"Added"
				}))
			else:
				self.response.out.write(simplejson.dumps({
					"status":"notAdded"
				}))
		else:
			self.error(403)

application = webapp.WSGIApplication([
	(r"/track/delete", DeleteTrackHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()