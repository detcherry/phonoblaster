from controllers.base import *

from django.utils import simplejson

from models.db.station import Station

class StationCheckHandler(BaseHandler):
	@login_required
	def post(self):
		stationID = self.request.get("station_id").lower()
		jsonResponse = {}
		
		existingStation = Station.all().filter("identifier",stationID).get()
		if(existingStation):
			jsonResponse["available"] = "False"
		else:
			jsonResponse["available"] = "True"
		self.response.out.write(simplejson.dumps(jsonResponse))

application = webapp.WSGIApplication([
	(r"/station/check", StationCheckHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()