from controllers import config
from controllers.facebook import parse_signed_request
from controllers.station.root import RootHandler

from models.api.station import StationApi
from models.db.station import Station

class StationPageHandler(RootHandler):
	# GET request when reloading iFrame App (login or logout events)
	def get(self):
		page_id = self.request.get("id")
		self.process(page_id)
		
	# POST request when Facebook initializes page content
	def post(self):		
		signed_request = self.request.get("signed_request")
		data = parse_signed_request(signed_request, config.FACEBOOK_APP_SECRET)		
		page_id = data["page"]["id"]
			
		self.process(page_id)
			
	def process(self, page_id):
		station = Station.get_by_key_name(page_id)

		if(station):
			self.station_proxy = StationApi(station.shortname)
			
			# Temporarily, we don't display any Facebook app. Instead we make a redirection to the station on phonoblaster.com
			self.render("station/page/redirect.html", None)
			
			"""
			TO BE REMOVED
			
			on_air = self.station_proxy.on_air()
			
			if(not on_air):
				self.render("station/page/off.html", None)
			else:
				self.render("station/page/on.html", None)
			"""
			
					
		else:
			self.render("station/page/404.html", None)