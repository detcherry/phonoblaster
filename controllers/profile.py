from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution

class ProfileHandler(BaseHandler):
	@login_required
	def get(self):
		self.user_station = Station.all().filter("creator", self.current_user.key()).get()
		user_contributions = Contribution.all().filter("contributor", self.current_user.key()).fetch(12)
		station_keys = [Contribution.station.get_value_for_datastore(c) for c in user_contributions]
		self.user_contributing_stations = db.get(station_keys)
		
		self.additional_template_values = {
			"user_station": self.user_station,
			"user_contributing_stations": self.user_contributing_stations,
		}
		self.render("../templates/user/user.html")

application = webapp.WSGIApplication([
	(r"/profile", ProfileHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()