from controllers.base import *

from django.utils import simplejson

from models.db.station import Station
from models.db.contribution import Contribution
from models.interface.station import InterfaceStation

class DeleteContributionHandler(BaseHandler):
	@login_required
	def post(self):
		contribution_key = self.request.get("contribution_key")
		contribution_to_delete = Contribution.get(contribution_key)
		station_key = Contribution.station.get_value_for_datastore(contribution_to_delete)
		contributor_to_delete_key = Contribution.contributor.get_value_for_datastore(contribution_to_delete)
		
		station_proxy = InterfaceStation(station_key = station_key)		
		response = station_proxy.delete_contributor(str(self.current_user.key()), contribution_key, contributor_to_delete_key)
		
		if response:
			self.response.out.write(simplejson.dumps({"status":"Deleted"}))
		else:
			self.response.out.write(simplejson.dumps({"status":"notDeleted"}))


application = webapp.WSGIApplication([
	(r"/contribution/delete", DeleteContributionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
