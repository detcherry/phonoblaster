import logging
from calendar import timegm

from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.interface.onair import InterfaceOnAir

class StationOnAirHandler(webapp.RequestHandler):
    def get(self):
		onair_proxy = InterfaceOnAir()
		onair_items = onair_proxy.stations_and_tracks

		output = [];
		for station, track in onair_items:
			output.append({
				"station_thumbnail": str(station.thumbnail.key()),
				"station_identifier": station.identifier,
				"youtube_thumbnail": track.youtube_thumbnail_url,
				"youtube_title": track.youtube_title,
			})
			
		data = {
			"items": output
		}
		self.response.out.write(simplejson.dumps(data))
		


application = webapp.WSGIApplication([
	(r"/station/onair", StationOnAirHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()		