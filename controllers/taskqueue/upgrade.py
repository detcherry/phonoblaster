import logging
import traceback
import sys
import webapp2

from datetime import datetime

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from models.api.station import StationApi

from models.db.broadcast import Broadcast

class UpgradeHandler(webapp2.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")
		
		q = Broadcast.all()
		q.order("created")
		
		# Is there a cursor?
		if(cursor):
			logging.info("Cursor found")
			q.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")
			
		broadcasts = q.fetch(50)
		
		if(len(broadcasts) > 0):
			track_keys = []
			tracks = []
			for b in broadcasts:
				track_keys.append(Broadcast.track.get_value_for_datastore(b))
			
			tracks = db.get(track_keys)
			
			to_put = []
			to_delete = []
			for b in broadcasts:
				
				found = False
				for t in tracks:
					key = Broadcast.track.get_value_for_datastore(b)
					if(t and t.key() == key):
						new_broadcast = Broadcast(
							key_name = b.key().name(),
							track = Broadcast.track.get_value_for_datastore(b),
							youtube_id = t.youtube_id,
							youtube_title = t.youtube_title,
							youtube_duration = t.youtube_duration,
							station = Broadcast.station.get_value_for_datastore(b),
							submitter = Broadcast.submitter.get_value_for_datastore(b),
							created = b.created,
						)
						to_put.append(new_broadcast)
						found = True
						break
				
				if not found:
					to_delete.append(b)
			
			if(len(to_put) > 0):
				db.put(to_put)
				logging.info("Broadcasts put")
				
			if(len(to_delete) > 0):
				db.delete(to_delete)
				logging.info("Broadcasts delete")
			
			cursor = q.cursor()
			task = Task(
				url = "/taskqueue/upgrade",
				params = {'cursor': cursor},
			)
			task.add(queue_name = "upgrade-queue")
		else:
			logging.info("No more broadcast to update")
			
			subject = "Upgrade of broadcast entities done"
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