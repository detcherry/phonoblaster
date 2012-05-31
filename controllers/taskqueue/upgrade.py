import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

from models.api.station import StationApi

from models.db.station import Station
from models.db.broadcast import Broadcast

class UpgradeHandler(webapp.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")
		typeUpgrade = self.request.get("typeUpgrade")

		if typeUpgrade == "buffer":

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
						params = {'typeUpgrade':'buffer', 'cursor':cursor},
						countdown = 1 ,
					)
				task.add(queue_name = "upgrade-queue")
			else:
				logging.info("No More stations, terminating buffer update, launching visits counter upgrade.")

				task = Task(
						url = "/taskqueue/upgrade",
						params = {'typeUpgrade':'visits'},
						countdown = 1 ,
					)
				task.add(queue_name = "upgrade-queue")

		elif typeUpgrade == 'visits':
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
					station_proxy = StationApi(station.shortname)
					views = station_proxy.number_of_views
					visits = station_proxy.number_of_visits
					incrementation_value = views - visits

					if incrementation_value > 0:
						station_proxy.increase_visits_counter()
						logging.info("Incrementing visits counter of station : "+station.shortname+" by : "+str(incrementation_value))
					else:
						logging.info("No need to increment visits counter of station : "+station.shortname)

				cursor = query.cursor()
				task = Task(
						url = "/taskqueue/upgrade",
						params = {'typeUpgrade':'visits', 'cursor':cursor},
						countdown = 1 ,
					)
				task.add(queue_name = "upgrade-queue")

			else:
				logging.info("No stations found. Terminating update")

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