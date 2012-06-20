from controllers.station.root import RootHandler
from models.api.station import StationApi

class StationPictureHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		facebook_id = self.station_proxy.station.key().name()
		facebook_url = "https://graph.facebook.com/"+ facebook_id +"/picture?type=large"		
		self.redirect(str(facebook_url))
	
