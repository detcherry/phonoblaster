import logging

from controllers.station.root import RootHandler

class StationBroadcastsHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = ""
		self.render("station/broadcasts.html", None)