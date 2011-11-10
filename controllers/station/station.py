from controllers.station.root import *

class StationHandler(RootStationHandler):
	def get(self, station_id):
		self.station_proxy = InterfaceStation(station_identifier = station_id)
		self.current_station = self.station_proxy.station
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			# Retrieve the number of listeners
			number_of_listeners = len(self.station_proxy.station_sessions)
			
			if(self.allowed_to_post or number_of_listeners < 100):
				logging.info("Allowed to post or station not too crowded")
				
				# When the user is not a contributor of the station he's currently on, it's useful to display his station
				self.user_station = None
				if(self.current_user):
					# Probably not efficient, will require a refactoring at some point using the memcache
					self.user_station = Station.all().filter("creator", self.current_user.key()).get()				
				
				self.additional_template_values = {
					"site_url": controllers.config.SITE_URL,
					"allowed_to_post": self.allowed_to_post,
					"status_creator": self.status_creator,
					"user_station": self.user_station,
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