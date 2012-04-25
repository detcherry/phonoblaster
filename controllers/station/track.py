import logging
from calendar import timegm

from controllers.station.secondary import SecondaryHandler
from models.db.track import Track
from models.api.station import StationApi

class TrackHandler(SecondaryHandler):
	def get(self, track_id)	:
		track = Track.get_by_id(int(track_id))
		
		if(track):
			logging.info("Track found on Phonoblaster")
			shortname = track.station.shortname
			self.station_proxy = StationApi(shortname)
			template_values = { "track": Track.get_extended_track(track), }
			
			user_agent = self.request.headers["User-Agent"]
			facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
			
			if(user_agent == facebook_agent):
				# Facebook linter 
				self.facebook_render("station/facebook/track.html", template_values)
			else:
				# Not Facebook linter
				self.render("station/track.html", template_values)
			
		else:
			logging.info("Track was not found on Phonoblaster")
			self.render("station/404.html", None)
		
		