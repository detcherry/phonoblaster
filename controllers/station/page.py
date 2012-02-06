from controllers import config
from controllers.facebook import parse_signed_request
from controllers.station.root import RootHandler

from models.api.station import StationApi
from models.db.station import Station

class StationPageHandler(RootHandler):
	def post(self):		
		signed_request = self.request.get("signed_request")
		data = parse_signed_request(signed_request, config.FACEBOOK_APP_SECRET)		
		page_id = data["page"]["id"]
			
		station = Station.get_by_key_name(page_id)

		if(station):
			self.station_proxy = StationApi(station.shortname)
			on_air = self.station_proxy.on_air()
			
			if(not on_air):
				self.render("station/page/off.html", None)
			else:
				self.render("station/page/on.html", None)
					
		else:
			self.render("station/page/404.html", None)
	
