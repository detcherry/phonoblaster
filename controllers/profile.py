from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution

class ProfileHandler(BaseHandler):
	@login_required
	def get(self):
		self.user_station = Station.all().filter("creator", self.current_user.key()).get()
		self.user_contributions = Contribution.all().filter("contributor", self.current_user.key()).fetch(12)
		
		self.additional_template_values = {
			"user_station": self.user_station,
			"user_contributions": self.user_contributions,
		}
		self.render("../templates/user/user.html")

application = webapp.WSGIApplication([
	(r"/profile", ProfileHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()