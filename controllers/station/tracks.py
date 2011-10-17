from datetime import datetime
from calendar import timegm
from django.utils import simplejson

from controllers.station.root import *

class StationTracksHandler(RootStationHandler):
	def get(self, station_id):
		self.station_proxy = InterfaceStation(station_identifier =  station_id)
		self.current_station = self.station_proxy.station
		
		if not self.current_station:
			self.redirect("/error/404")
		else:
			tracks_per_page = 10
			
			query = Track.all().filter("station", self.current_station.key()).filter("expired <", datetime.now()).order("-expired")
			
			self.next =  None
			self.tracks = query.fetch(tracks_per_page + 1)
			if(len(self.tracks) == tracks_per_page +1):
				self.next = timegm(self.tracks[-2].expired.utctimetuple())
			self.tracks = self.tracks[:tracks_per_page]
			
			self.additional_template_values = {
				"tracks": self.tracks,
				"next": self.next,
			}
			self.render("../../templates/station/tracks.html")
		
	def post(self, station_id):
		tracks_per_page = 10
		
		self.station_proxy = InterfaceStation(station_identifier =  station_id)
		self.current_station = self.station_proxy.station
		self.next = datetime.utcfromtimestamp(int(self.request.get("next")))
		query = Track.all().filter("station", self.current_station.key()).filter("expired <", self.next).order("-expired")
		
		self.tracks = query.fetch(tracks_per_page + 1)
		if(len(self.tracks) == tracks_per_page + 1):
			self.next = timegm(self.tracks[-2].expired.utctimetuple())
		else:
			self.next = None
		self.tracks = self.tracks[:tracks_per_page]
				
		output = []
		for track in self.tracks:
			output.append({
				"id": track.youtube_id,
				"title": track.youtube_title,
				"thumbnail": track.youtube_thumbnail_url,
				"duration": track.youtube_duration,
			})
		
		data = {
			"next": self.next,
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