import logging

from controllers.station.root import RootHandler

from models.api.station import StationApi

class StationHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		
		if(self.station_proxy.station):
			admin = self.is_admin
			on_air = self.station_proxy.on_air()
			
			# If station not on air and user not admin, redirect to the broadcasts page
			if(not admin and not on_air):
				self.redirect("/" + shortname + "/broadcasts")
			else:
				template_values = {
					"is_admin": self.is_admin,
				}
				self.render("station/station.html", template_values)

		else:
			self.render("station/404.html", None)