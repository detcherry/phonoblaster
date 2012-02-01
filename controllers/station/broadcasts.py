from controllers.station.root import RootHandler

from models.api.station import StationApi

class StationBroadcastsHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		
		if(self.station_proxy.station):
			on_air = self.station_proxy.on_air()
			
			if(on_air):
				self.redirect("/"+shortname)
			else:
				self.render("station/off.html", None)
			
		else:
			self.render("station/404.html", None)