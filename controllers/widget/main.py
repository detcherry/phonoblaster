import os
from datetime import datetime
from datetime import timedelta
from calendar import timegm

from django.utils import simplejson

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from controllers import config
from models.queue import Queue
from models.db.station import Station
from models.db.session import Session

class WidgetCreationHandler(webapp.RequestHandler):
	def get(self):
		identifier = self.request.get('identifier')
		station = Station.all().filter("identifier", identifier).get()	
		
		template_values = {
			'station':station,
			'site_url': config.SITE_URL,
		}
							
		path = os.path.join(os.path.dirname(__file__), '../../templates/widget.html')
		self.response.out.write(template.render(path, template_values))
	
class WidgetConfigureHandler(webapp.RequestHandler):
	def get(self):
		identifier = self.request.get('identifier')
		station = Station.all().filter("identifier", identifier).get()
		queue = Queue(station.key())
		tracks = queue.getTracks()
		
		# Get the number of listeners
		q = Session.all()
		q.filter("station", station.key())
		q.filter("ended", None)
		q.filter("created >", datetime.now() - timedelta(0,7200))
		number_listeners = q.count()
		
		if len(tracks) > 0:
			self.response.out.write(simplejson.dumps({"status":"Yes","tracks":[track.to_dict() for track in tracks],"listeners":number_listeners}))
		else:
			self.response.out.write(simplejson.dumps({"status":"No","listeners":number_listeners}))

class WidgetHistoryHandler(webapp.RequestHandler):
	def get(self):
		identifier = self.request.get('identifier')
		station = Station.all().filter("identifier", identifier).get()
		queue = Queue(station.key())
		tracks = queue.getRecentHistory(6)
		
		if len(tracks) > 0:
			self.response.out.write(simplejson.dumps({"status":"Yes","tracks":[track.to_dict() for track in tracks]}))
		else:
			self.response.out.write(simplejson.dumps({"status":"No"}))


application = webapp.WSGIApplication([
	("/plugin/widget/init", WidgetCreationHandler),
	("/plugin/widget/configure", WidgetConfigureHandler),
	("/plugin/widget/history", WidgetHistoryHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
