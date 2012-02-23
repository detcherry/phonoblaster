import logging

from base import BaseHandler
from controllers import facebook
from models.db.station import Station

class HomeHandler(BaseHandler):
	def get(self):
		if(self.user_proxy):
			
			stations = self.user_proxy.stations
			if(len(stations) == 0):
				# Redirect to the creation page
				self.redirect("/station/create")
			else:
				if(len(stations) == 1):
					# Redirect to the station
					station = stations[0]
					self.redirect("/" + station.shortname)
				else:
					# Display all the stations
					template_values = {
						"user_stations": stations,
					}
					self.render("home.html", template_values)
			
		else:
			self.render("welcome.html", None)