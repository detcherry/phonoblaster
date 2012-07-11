import re
import logging

from controllers.station.root import RootHandler
from models.db.broadcast import Broadcast
from models.api.station import StationApi

class BroadcastHandler(RootHandler):
	def get(self, key_name):
		broadcast = Broadcast.get_by_key_name(key_name)
		
		if(broadcast):
			m = re.match(r"(\w+).(\w+)", key_name)
			shortname = m.group(1)			
			self.station_proxy = StationApi(shortname)
			
			user_agent = self.request.headers["User-Agent"]
			facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
			
			if(user_agent != facebook_agent):
				# Redirect to station
				self.redirect("/" + shortname)
			else:
				# Facebook linter
				station = self.station_proxy.station
				template_values = {
					"broadcast" : broadcast,
				}
				self.render("station/facebook/broadcast.html", template_values)
		else:
			# 404 error
			self.render("station/404.html", None)