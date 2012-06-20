import logging
import traceback
import sys
import webapp2

from datetime import datetime

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.api.station import StationApi

from models.db.station import Station
from models.db.broadcast import Broadcast

class UpgradeHandler(webapp2.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")
		
		query = Station.all()
		# Is there a cursor?
		if(cursor):
			logging.info("Cursor found")
			query.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")
		
		stations = query.fetch(100)
		
		if(len(stations) > 0):
			for station in stations:
				if station.full is None and station.thumb is None:
					station.full = "/static/images/backgrounds/full/webradio.png"
					station.thumb = "/static/images/backgrounds/thumb/webradio.png"
		
			db.put(stations)
			logging.info("Putting new stations in datastore")
	
			cursor = query.cursor()
			task = Task(
				url = "/taskqueue/upgrade",
				params = {'cursor': cursor},
				countdown = 1 ,
			)
			task.add(queue_name = "upgrade-queue")
		else:
			logging.info("No more stations to fill background for")
			
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

"""
# Buffer Upgrade

class UpgradeHandler(webapp2.RequestHandler):
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
					broadcasts = q.fetch(100)
					logging.info("Broadcast retrieved from datastore")

					# We want to add only broadcasts associated to different tracks.
					track_keys = []
					broadcast_keys = []
					for b in broadcasts:
						broadcast_keys.append(b.key())
						track_keys.append(b.track.key())

					# Removing doubloons
					track_keys_unique = list(set(track_keys))
					broadcast_keys_unique = []

					while len(track_keys_unique)>0:
						t = track_keys_unique.pop(0)

						for i in xrange(0,len(broadcasts)):
							b = broadcasts[i]

							if b.track.key() == t:
								broadcast_keys_unique.append(b.key())
								break

					station.broadcasts = broadcast_keys_unique[:30] # A maximum of 30 broadcasts in the buffer
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
						station_proxy.increase_visits_counter(incrementation_value)
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
"""