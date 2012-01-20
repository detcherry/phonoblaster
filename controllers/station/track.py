from controllers.station.root import RootHandler

from models.db.track import Track

from models.api.station import StationApi

class StationTrackHandler(RootHandler):
	def get(self, shortname, track_id):
		self.station_proxy = StationApi(shortname)
		track = Track.get_by_id(int(track_id))
		
		station = self.station_proxy.station
		station_key = station.key()
		track_station_key = Track.station.get_value_for_datastore(track)
		extended_track = Track.get_extended_tracks([track])[0]
		
		if(not station or not track or station_key != track_station_key or not extended_track):
			self.render("station/404.html", None)		
		else:
			template_values = {
				"track": extended_track,
			}
			self.render("station/track.html", template_values)

		
		
		