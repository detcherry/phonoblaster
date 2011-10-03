from datetime import datetime
from datetime import timedelta
from time import gmtime
from calendar import timegm
from random import randrange

from controllers.station.root import *

from google.appengine.api import channel


class StationHandler(RootStationHandler):
	def get(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		if not self.current_station:
			self.error(404)
		else:			
			self.additional_template_values = {
				"site_url": controllers.config.SITE_URL,
				"allowed_to_post": self.allowed_to_post,
				"status_creator": self.status_creator,
			}		
			self.render("../../templates/station/station.html")
				

application = webapp.WSGIApplication([
	(r"/(\w+)", StationHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()