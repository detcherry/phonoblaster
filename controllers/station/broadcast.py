import re

from controllers.station.secondary import SecondaryHandler
from models.db.broadcast import Broadcast
from models.api.station import StationApi

class BroadcastHandler(SecondaryHandler):
	def get(self, key_name):
		broadcast = Broadcast.get_by_key_name(key_name)
		
		if(broadcast):
			
			m = re.match(r"(\w+).(\w+)", key_name)
			shortname = m.group(1)			
			self.station_proxy = StationApi(shortname)
			
			user_agent = self.request.headers["User-Agent"]
			facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
			
			queue = self.station_proxy.queue
			
			if(user_agent != facebook_agent and len(queue) > 0 and queue[0]["key_name"] == key_name):	
				# Redirect to live
				self.redirect("/" + shortname)
			
			else:
				# Render the broadcast page
				station = self.station_proxy.station
				extended_broadcast = Broadcast.get_extended_broadcasts([broadcast], station)[0]
				template_values = {
					"broadcast": extended_broadcast,
				}
				self.render("station/broadcast.html", template_values)
		
		else:
			self.redirect("station/404.html", None)