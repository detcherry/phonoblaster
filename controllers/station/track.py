from controllers.station.secondary import SecondaryHandler
from models.db.track import Track
from models.api.station import StationApi

class TrackHandler(SecondaryHandler):
	def get(self, track_id)	:
		track = Track.get_by_id(int(track_id))
		
		if(track):
			shortname = track.station.shortname
			self.station_proxy = StationApi(shortname)
			extended_track = Track.get_extended_tracks([track])[0]
			template_values = {
				"track": extended_track,
			}
			self.render("station/track.html", template_values)
			
		else:
			self.render("station/404.html", None)
		
		