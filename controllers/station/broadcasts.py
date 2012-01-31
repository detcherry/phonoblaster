from controllers.station.root import RootHandler

from models.api.station import StationApi

class StationBroadcastsHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		self.render("station/broadcasts.html", None)