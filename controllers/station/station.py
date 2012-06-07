import logging

from base import profile_required

from controllers.station.root import RootHandler

from models.api.station import StationApi

class StationHandler(RootHandler):
	@profile_required
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		
		if(self.station_proxy.station):
			admin = self.is_admin
			self.render("station/station.html", None)
			
			"""
			TO BE REMOVED
			
			on_air = self.station_proxy.on_air()
			
			# If station not on air and user not admin, redirect to the broadcasts page
			if(not admin and not on_air):
				self.render("station/off.html", None)
			else:
				self.render("station/on.html", None)
			"""
		else:
			self.render("station/404.html", None)