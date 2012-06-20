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