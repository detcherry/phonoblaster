import logging
import webapp2

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.db.station import Station

class UpgradeHandler(webapp2.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")
		
		q = Station.all()
		q.order("updated")
		
		# Is there a cursor?
		if(cursor):
			logging.info("Cursor found")
			q.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")
		
		stations = q.fetch(50)
		
		to_put = []
		done = False
		for s in stations:
			if s.active is None:
				s.active = s.updated
				to_put.append(s)
			else:
				done = True
				break
		
		db.put(to_put)
		logging.info("Station entities updated")
			
		if not done:
			logging.info("Starting another task")
			
			new_cursor = q.cursor()
			task = Task(
				url = "/taskqueue/upgrade",
				params = {
					'cursor': new_cursor,
				},
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