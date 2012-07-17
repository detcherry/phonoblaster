import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from google.appengine.ext import db

class StationManageHandler(BaseHandler):
	@login_required
	def get(self):
		template_values = {}
		
		user_stations = db.get(self.user_proxy.user.stations)
		installed_stations = []
		
		for user_station in user_stations:
			if(user_station is not None and user_station.type == "page"):
				installed_stations.append(user_station)
		
		if(len(installed_stations) > 0):
			template_values = {
				"installed_stations": installed_stations,
			}
		
			self.render("station/manage.html", template_values)
		else:
			self.redirect("/")