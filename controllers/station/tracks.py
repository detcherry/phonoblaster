from datetime import datetime
from django.utils import simplejson

from controllers.station.root import *

class StationTracksHandler(RootStationHandler):
	def get(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		query = Track.all().filter("station", self.current_station.key()).filter("expired <", datetime.now()).order("-expired")
		self.tracks = query.fetch(10)
		self.offset = 10
		
		self.older_tracks = False
		if(self.tracks and (len(self.tracks) == 10)):
			self.older_tracks = True
		
		if not self.current_station:
			self.error(404)
		else:
			self.additional_template_values = {
				"tracks": self.tracks,
				"offset": self.offset,
				"older_tracks": self.older_tracks,
			}
			self.render("../../templates/station/tracks.html")
		
	def post(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		query_offset = int(self.request.get("offset"))
				
		query = Track.all().filter("station", self.current_station.key()).filter("expired <", datetime.now()).order("-expired")
		tracks = query.fetch(10, offset = query_offset)
		new_offset = query_offset + 10
				
		output = []
		for track in tracks:
			output.append({
				"id": track.youtube_id,
				"title": track.youtube_title,
				"thumbnail": track.youtube_thumbnail_url,
				"duration": track.youtube_duration,
			})
		
		data = {
			"offset": new_offset,
			"tracks": output,
		}
		
		self.response.out.write(simplejson.dumps(data));	
			

application = webapp.WSGIApplication([
	(r"/(\w+)/tracks", StationTracksHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()