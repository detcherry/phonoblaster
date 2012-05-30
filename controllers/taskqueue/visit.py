import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.db.track import Track
from models.db.view import View
from models.db.air import Air
from models.api.station import StationApi
from google.appengine.api.taskqueue import Task

class VisitHandler(webapp.RequestHandler):
	def post(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)

		if station_proxy.station:
			# Station exists in database, now proceeding to increasing counter
			station_proxy.increase_visits_counter(1)
			logging.info("Increased visits counter for station : "+shortname)
		
application = webapp.WSGIApplication([
	(r"/taskqueue/visit", VisitHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()