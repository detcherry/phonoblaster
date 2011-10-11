from datetime import datetime
from datetime import timedelta
from time import gmtime
from calendar import timegm
from random import randrange

from controllers.station.root import *

class StationHandler(RootStationHandler):
	def get(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			# Retrieve the number of listeners
			q = Session.all()
			q.filter("station", self.current_station.key())
			q.filter("ended", None)
			q.filter("created >", datetime.now() - timedelta(0,7200))
			number_of_listeners = q.count()
			
			if(number_of_listeners <= 100):
				self.additional_template_values = {
					"site_url": controllers.config.SITE_URL,
					"allowed_to_post": self.allowed_to_post,
					"status_creator": self.status_creator,
				}		
				self.render("../../templates/station/station.html")
			else:
				self.additional_template_values = {}
				self.render("../../templates/station/toocrowded.html")
				

application = webapp.WSGIApplication([
	(r"/(\w+)", StationHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()