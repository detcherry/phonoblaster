import logging

from controllers.station.root import RootHandler

from models.api.station import StationApi

class StationHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		
		if(self.station_proxy.station):
			self.render("station/station.html", None)
		else:
			self.render("station/404.html", None)