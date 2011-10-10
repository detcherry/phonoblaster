from controllers.station.root import *

class StationContributorsHandler(RootStationHandler):
	def get(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			if(len(self.current_contributions) < 10):
				some_contributions_left = True
			else:
				some_contributions_left = False
				
			self.additional_template_values = {
				"status_creator": self.status_creator,
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