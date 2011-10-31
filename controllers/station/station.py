from datetime import datetime
from datetime import timedelta
from time import gmtime
from calendar import timegm
from random import randrange

from controllers.station.root import *

class StationHandler(RootStationHandler):
	def get(self, station_id):
		self.station_proxy = InterfaceStation(station_identifier = station_id)
		self.current_station = self.station_proxy.station
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			# When you're the station creator or a contributor, you'll always have access to!
			if(self.allowed_to_post):
				logging.info("Allowed to post, doesn't matter if station too crowded")
				self.additional_template_values = {
					"site_url": controllers.config.SITE_URL,
					"allowed_to_post": self.allowed_to_post,
					"status_creator": self.status_creator,
				}		
				self.render("../../templates/station/station.html")
				
			else:
				# Retrieve the number of listeners
				number_of_listeners = len(self.station_proxy.station_sessions)
			
				if(number_of_listeners < 100):
					logging.info("Number of listeners < 100")
					self.additional_template_values = {
						"site_url": controllers.config.SITE_URL,
						"allowed_to_post": self.allowed_to_post,
						"status_creator": self.status_creator,
					}		
					self.render("../../templates/station/station.html")
				else:
					logging.info("Number of listeners > 100, station too crowded")
					self.additional_template_values = {}
					self.render("../../templates/station/toocrowded.html")
				

application = webapp.WSGIApplication([
	(r"/(\w+)", StationHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()