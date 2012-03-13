import logging

from controllers.station.secondary import SecondaryHandler
from models.db.track import Track
from models.api.station import StationApi

class TrackHandler(SecondaryHandler):
	def get(self, track_id)	:
		track = Track.get_by_id(int(track_id))
		
		if(track):
			shortname = track.station.shortname
			self.station_proxy = StationApi(shortname)
			
			tracks = [track]
			extended_tracks = Track.get_extended_tracks(tracks)
			
			if extended_tracks:
				logging.info("Youtube track exists")
				extended_track = extended_tracks[0]
				template_values = {
					"track": extended_track,
				}
				
				user_agent = self.request.headers["User-Agent"]
				facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
				
				if(user_agent == facebook_agent):
					# Facebook linter 
					self.facebook_render("station/facebook/track.html", template_values)
				else:
					# Not Facebook linter
					self.render("station/track.html", template_values)
				
			else:
				logging.error("Youtube track does not exist anymore")
				self.redirect("/" + shortname)
			
		else:
			self.render("station/404.html", None)
		
		