import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

from models.db.station import Station
from models.db.broadcast import Broadcast

class UpgradeHandler(webapp.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")

		query = Station.all()
		# Is there a cursor?
		if(cursor):
			logging.info("Cursor found")
			query.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")

		stations = query.fetch(10)

		if(stations):
			logging.info("Stations found")
			
			for i in xrange(0,len(stations)):
				station = stations[i]

				# Now we need to retrieve 30 latest broadcasts from datastore
				q = Broadcast.all()
				q.filter("station", station).order("-created")
				broadcast_keys = q.fetch(30, keys_only=True) # We are only interested in the keys of the entities, not the entire entities.
				logging.info("Broadcast Keys retrieved from datastore")
				station.broadcasts = broadcast_keys
				station.timestamp = datetime.utcnow()

			# Putting stations in datastore
			db.put(stations)
			logging.info("Putting new stations in datastore")

			cursor = query.cursor()
			task = Task(
					url = "/taskqueue/upgrade",
					params = {'cursor':cursor},
					countdown = 1 ,
				)
			task.add(queue_name = "upgrade-queue")
		else:
			logging.info("No More stations, terminating update")

			subject = "Upgrade from queue to buffer done"
			body = "Everything is OK"
			
			task = Task(
				url = "/taskqueue/mail",
				params = {
					"to": "activity@phonoblaster.com",
					"subject": subject,
					"body": body,
				}
			)
			task.add(queue_name = "worker-queue")





application = webapp.WSGIApplication([
	(r"/taskqueue/upgrade", UpgradeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	