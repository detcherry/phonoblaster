from controllers.base import *

from django.utils import simplejson

from models.interface.station import InterfaceStation

class StationCheckHandler(BaseHandler):
	@login_required
	def post(self):
		station_id = self.request.get("station_id").lower()
		json_response = {}
		existing_station = None
		
		if(station_id):
			station_proxy = InterfaceStation(station_identifier = station_id)
			existing_station = station_proxy.station
		
		if(existing_station):
			json_response["available"] = "False"
		else:
			json_response["available"] = "True"
		self.response.out.write(simplejson.dumps(json_response))


application = webapp.WSGIApplication([
	(r"/station/check", StationCheckHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()