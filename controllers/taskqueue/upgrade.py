import logging
import traceback
import sys
import webapp2

from datetime import datetime

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.api.station import StationApi
from models.db.station import Station
#from models.db.broadcast import Broadcast

class UpgradeHandler(webapp2.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")
		
		q = Station.all()
		q.order("created")
		
		# Is there a cursor?
		if(cursor):
			logging.info("Cursor found")
			q.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")
		
		stations = q.fetch(2)
		
		if(len(stations) > 0):
			
			to_put = []
			for s in stations:
				s.online = False
				to_put.append(s)
			
			db.put(to_put)
			logging.info("Station entities updated")
			
			cursor = q.cursor()
			task = Task(
				url = "/taskqueue/upgrade",
				params = {'cursor': cursor},
			)
			task.add(queue_name = "upgrade-queue")
		else:
			logging.info("No more station to update")
			
			subject = "Upgrade of station entities done"
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
