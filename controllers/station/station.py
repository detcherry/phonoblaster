import logging

from controllers.station.root import RootHandler

from models.api.station import StationApi

class StationHandler(RootHandler):
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
		
		if(self.station_proxy.station):
			# If station not on air and user not admin, redirect to the broadcasts page
			#if(not self.is_admin and not self.station_proxy.on_air):
			#	self.redirect("/" + shortname + "/broadcasts")
			#else:
			#	template_values = {
			#		"is_admin": self.is_admin,
			#	}
			#	self.render("station/station.html", template_values)
			template_values = {
					"is_admin": self.is_admin,
			}
			self.render("station/station.html", template_values)
		else:
			self.render("station/404.html", None)