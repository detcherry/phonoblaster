import os
from datetime import datetime
from datetime import timedelta
from calendar import timegm

from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers import config
from models.interface.station import InterfaceStation
from models.db.station import Station
from models.db.session import Session
from models.db.track import Track

class WidgetCreationHandler(webapp.RequestHandler):
	def get(self):
		identifier = self.request.get('identifier')
		station_proxy = InterfaceStation(station_identifier = identifier)
		station = station_proxy.station
		
		template_values = {
			'station': station,
			'site_url': config.SITE_URL,
		}
							
		path = os.path.join(os.path.dirname(__file__), '../../templates/widget.html')
		self.response.out.write(template.render(path, template_values))
	
class WidgetConfigureHandler(webapp.RequestHandler):
	def get(self):
		identifier = self.request.get('identifier')
		station_proxy = InterfaceStation(station_identifier = identifier)
		station = station_proxy.station
		tracks = station_proxy.station_tracklist
		number_listeners = len(station_proxy.station_sessions)
		
		if len(tracks) > 0:
			self.response.out.write(simplejson.dumps({"status":"Yes","tracks":[track.to_dict() for track in tracks],"listeners":number_listeners}))
		else:
			self.response.out.write(simplejson.dumps({"status":"No","listeners":number_listeners}))

class WidgetHistoryHandler(webapp.RequestHandler):
	def get(self):
		identifier = self.request.get('identifier')		
		station_proxy = InterfaceStation(station_identifier = identifier)
		station = station_proxy.station
		
		q = Track.all()
		q.filter("station",station.key())
		q.filter("expired <", datetime.now())
		q.order("-expired")
		last_tracks = q.fetch(6)
		
		if len(last_tracks) > 0:
			self.response.out.write(simplejson.dumps({"status":"Yes","tracks":[track.to_dict() for track in last_tracks]}))
		else:
			self.response.out.write(simplejson.dumps({"status":"No"}))


application = webapp.WSGIApplication([
	("/widget/init", WidgetCreationHandler),
	("/widget/configure", WidgetConfigureHandler),
	("/widget/history", WidgetHistoryHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
