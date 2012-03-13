import re
import logging

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
				station = self.station_proxy.station
				broadcasts = [broadcast]
				extended_broadcasts = Broadcast.get_extended_broadcasts(broadcasts, station)
				
				if extended_broadcasts:
					logging.info("Youtube track was found")
					
					# Youtube track exists
					extended_broadcast = extended_broadcasts[0]
					template_values = {
						"broadcast": extended_broadcast,
					}
					
					if(user_agent == facebook_agent):
						# Facebook linter
						self.facebook_render("station/facebook/broadcast.html", template_values)
					else:
						# Not Facebook linter
						self.render("station/broadcast.html", template_values)
				
				else:
					logging.info("Youtube track was not found")
					self.redirect("/" + shortname)
		
		else:
			self.render("station/404.html", None)