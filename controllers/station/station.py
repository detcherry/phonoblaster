import logging

from controllers.station.root import RootHandler

class StationHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = ""
		self.render("station/station.html", None)