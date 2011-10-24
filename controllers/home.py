from datetime import datetime

from controllers.base import *

from models.db.station import Station
from models.db.contribution import Contribution

class HomeHandler(BaseHandler):
    def get(self):
		current_user_station = None
		# We get the user station
		if(self.current_user):
			current_user_station = Station.all().filter("creator", self.current_user.key()).get()
		
		# We get the stations where the user contributes
		current_user_contributing_stations = None
		if(self.current_user):
			current_user_contributions = Contribution.all().filter("contributor", self.current_user.key()).fetch(12)
			station_keys = [Contribution.station.get_value_for_datastore(c) for c in current_user_contributions]
			current_user_contributing_stations = db.get(station_keys)
		
		
		# If user is logged in, we fetched up to 48 stations. Otherwise just 12
		if(self.current_user):
			number_of_stations_to_fetch = 48
		else:
			number_of_stations_to_fetch = 12
			
		# We get the active or non active stations	
		active_stations = Station.all().filter("active >", datetime.now()).order("-active").fetch(number_of_stations_to_fetch)
		non_active_stations = None
		if(len(active_stations) == 0):
			non_active_stations = Station.all().order("-active").fetch(number_of_stations_to_fetch)
		
		
		self.additional_template_values = {
			"site_url": controllers.config.SITE_URL,
			"current_user_station": current_user_station,
			"active_stations": active_stations,
			"non_active_stations": non_active_stations,
			"current_user_contributing_stations": current_user_contributing_stations,
		}
		self.render("../templates/home.html")
		
application = webapp.WSGIApplication([
	(r"/", HomeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()