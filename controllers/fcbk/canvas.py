from datetime import datetime

from controllers.base import *

from models.db.request import FcbkRequest
from models.db.station import Station

class CanvasHandler(BaseHandler):
	def get(self):
		# As I noticed Facebook was sometimes doing GET sometimes POST requests, I copy pasted the code in both handlers
		request_ids = self.request.get("request_ids").split(",")
		fcbkrequests = FcbkRequest.all().order("-created").filter("fcbk_id IN", request_ids).fetch(1000)
		requester_keys = [FcbkRequest.requester.get_value_for_datastore(f) for f in fcbkrequests]
		station_keys = [FcbkRequest.station.get_value_for_datastore(f) for f in fcbkrequests]
		requesters = db.get(requester_keys)
		stations = db.get(station_keys)
		self.requests = zip(requesters, stations)
		
		try:
			request_ids.remove('')
		except:
			logging.info("Facebook Requests: " + str(request_ids))
		
		if(len(request_ids) > 0):
			self.additional_template_values = {
				"requests": self.requests,
				"site_url": controllers.config.SITE_URL
			}
			self.render("../templates/facebook/canvas.html")
		else:
			current_user_station = None
			
			active_stations = Station.all().filter("active >", datetime.now()).order("-active").fetch(18)
			non_active_stations = None
			if(len(active_stations) == 0):
				non_active_stations = Station.all().order("-active").fetch(18)
			
			self.additional_template_values = {
				"current_user_station": current_user_station,
				"active_stations": active_stations,
				"non_active_stations": non_active_stations,
				"site_url": controllers.config.SITE_URL,
			}
			self.render("../templates/facebook/home.html")

	def post(self):
		request_ids = self.request.get("request_ids").split(",")
		fcbkrequests = FcbkRequest.all().order("-created").filter("fcbk_id IN", request_ids).fetch(1000)
		requester_keys = [FcbkRequest.requester.get_value_for_datastore(f) for f in fcbkrequests]
		station_keys = [FcbkRequest.station.get_value_for_datastore(f) for f in fcbkrequests]
		requesters = db.get(requester_keys)
		stations = db.get(station_keys)
		self.requests = zip(requesters, stations)

		try:
			request_ids.remove('')
		except:
			logging.info("Facebook Requests: " + str(request_ids))

		if(len(request_ids) > 0):
			self.additional_template_values = {
				"requests": self.requests,
				"site_url": controllers.config.SITE_URL
			}
			self.render("../templates/facebook/canvas.html")
		else:
			current_user_station = None

			active_stations = Station.all().filter("active >", datetime.now()).order("-active").fetch(18)
			non_active_stations = None
			if(len(active_stations) == 0):
				non_active_stations = Station.all().order("-active").fetch(18)

			self.additional_template_values = {
				"current_user_station": current_user_station,
				"active_stations": active_stations,
				"non_active_stations": non_active_stations,
				"site_url": controllers.config.SITE_URL,
			}
			self.render("../templates/facebook/home.html")
	
application = webapp.WSGIApplication([
	(r"/facebook/canvas/", CanvasHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()