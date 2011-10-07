from datetime import datetime

from controllers.base import *

from models.db.station import Station
from models.db.contribution import Contribution

class HomeHandler(BaseHandler):
    def get(self):
		current_user_station = None
		if(self.current_user):
			current_user_station = Station.all().filter("creator", self.current_user.key()).get()
						
		active_stations = Station.all().filter("active >", datetime.now()).order("-active").fetch(48)
		non_active_stations = None
		if(len(active_stations) == 0):
			non_active_stations = Station.all().order("-active").fetch(48)
		
		current_user_contributing_stations = None
		if(self.current_user):
			current_user_contributions = Contribution.all().filter("contributor", self.current_user.key()).fetch(12)
			station_keys = [Contribution.station.get_value_for_datastore(c) for c in current_user_contributions]
			current_user_contributing_stations = db.get(station_keys)
		
		self.additional_template_values = {
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