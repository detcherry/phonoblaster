import logging

from controllers.station.root import RootHandler
from models.db.track import Track
from models.api.station import StationApi

class TrackHandler(RootHandler):
	def get(self, track_id)	:
		track = Track.get_by_id(int(track_id))
		
		if(track):
			logging.info("Track found on Phonoblaster")
			shortname = track.station.shortname
			
			user_agent = self.request.headers["User-Agent"]
			facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
			
			if(user_agent != facebook_agent):
				# Redirect to live station
				self.redirect("/" + shortname)
				
			else:
				# Facebook linter 
				self.station_proxy = StationApi(shortname)
				template_values = { 
					"track": track,
				}
				
				self.render("station/facebook/track.html", template_values)
		else:
			# 404 error
			self.render("station/404.html", None)
		
		