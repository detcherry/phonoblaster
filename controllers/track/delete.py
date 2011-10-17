from datetime import datetime
from datetime import timedelta

from controllers.base import *

from django.utils import simplejson

from models.db.station import Station
from models.db.track import Track
from models.db.session import Session
from models.interface.station import InterfaceStation

from google.appengine.api.taskqueue import Task

class DeleteTrackHandler(BaseHandler):
	@login_required
	def post(self):
		phonoblaster_id = self.request.get("id")
		station_key = self.request.get("station_key")
		
		station_proxy = InterfaceStation(station_key = station_key)
		response = station_proxy.delete_track(str(self.current_user.key()), phonoblaster_id)
		if(response):
			# Build the data
			self.data = {
				"type":"tracklist_delete",
				"content": phonoblaster_id,
			}
			# Send a message to everybody
			task = Task(
				url = "/taskqueue/notify",
				params = { 
					"station_key": station_key,
					"data": simplejson.dumps(self.data),
					"excluded_channel_id": "",
				},
			)
			task.add(
				queue_name = "tracklist-queue-1"
			)
			self.response.out.write(simplejson.dumps({"status":"Deleted"}))
		else:
			self.response.out.write(simplejson.dumps({"status":"notDeleted"}))
			

application = webapp.WSGIApplication([
	(r"/track/delete", DeleteTrackHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()