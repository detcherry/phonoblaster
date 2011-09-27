from controllers.base import *

from models.db.station import Station
from models.db.contribution import Contribution

class DeleteContributionHandler(BaseHandler):
	@login_required
	def post(self):
		station_id = self.request.get("station_id")
		contribution_key = self.request.get("key")
		contribution = Contribution.get(contribution_key)
		
		if(contribution.station.creator.key() == self.current_user.key()):
			contribution.delete()
		else:
			self.error(403)

application = webapp.WSGIApplication([
	(r"/contribution/delete", DeleteContributionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
