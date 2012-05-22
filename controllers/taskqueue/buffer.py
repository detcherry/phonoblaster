import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

from models.api.station import StationApi

class BufferDeleteHandler(webapp.RequestHandler):
	def post(self):
		shortname = self.request.get('station')
		id_track_to_delete = self.request.get('id')
		logging.info(shortname)
		logging.info(id_track_to_delete)

		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			result = station_proxy.remove_track_from_buffer(id_track_to_delete)
			logging.info(result)

class BufferChangeHandler(webapp.RequestHandler):
	def post(self):
		shortname = self.request.get("shortname")
		old_index = self.request.get("old_index")
		new_index = self.request.get("new_index")

		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			result = station_proxy.remove_track_from_buffer(old_index, new_index)
			logging.info(result)


application = webapp.WSGIApplication([
	(r"/taskqueue/buffer/delete", BufferDeleteHandler),
	(r"/taskqueue/buffer/change", BufferChangeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	