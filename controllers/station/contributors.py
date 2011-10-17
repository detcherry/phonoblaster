from controllers.station.root import *

class StationContributorsHandler(RootStationHandler):
	def get(self, station_id):
		self.station_proxy = InterfaceStation(station_identifier =  station_id)
		self.current_station = self.station_proxy.station
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			# Get contributions and contributors (we probably have contributors in memcache but not contributions...)
			current_station_contributions = Contribution.all().filter("station", self.current_station.key()).fetch(10)
			user_keys = [Contribution.contributor.get_value_for_datastore(c) for c in current_station_contributions]
			current_station_contributors = db.get(user_keys)
			self.current_contributions = zip(current_station_contributions, current_station_contributors)
			
			if(len(self.current_contributions) < 10):
				some_contributions_left = True
			else:
				some_contributions_left = False
				
			self.additional_template_values = {
				"status_creator": self.status_creator,
				"current_contributions": self.current_contributions,
				"some_contributions_left": some_contributions_left,
			}
			self.render("../../templates/station/contributors.html")

application = webapp.WSGIApplication([
	(r"/(\w+)/contributors", StationContributorsHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()