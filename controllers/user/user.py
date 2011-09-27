from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution

class UserHandler(BaseHandler):
	def get(self, user_id):
		self.user_visited = User.get_by_id(int(user_id))
		
		if not self.user_visited:
			self.error(404)
		else:
			
			self.user_station = Station.all().filter("creator", self.user_visited.key()).get()
			self.user_contributions = Contribution.all().filter("contributor", self.user_visited.key())
			
			self.additional_template_values = {
				"user_visited": self.user_visited,
				"user_station": self.user_station,
				"user_contributions": self.user_contributions,
			}
			self.render("../templates/user/user.html")
		
		

application = webapp.WSGIApplication([
	(r"/user/(\w+)", UserHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()