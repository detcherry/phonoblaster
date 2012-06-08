import logging
from datetime import datetime

import django_setup
from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.track import Track
from models.db.broadcast import Broadcast
from models.db.like import Like

from models.api.station import StationApi

class ApiTracksHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		offset = self.request.get("offset")
		station_proxy = StationApi(shortname)
		
		if(station_proxy.station and offset):
			extended_tracks = station_proxy.get_tracks(datetime.utcfromtimestamp(int(offset)))
			self.response.out.write(json.dumps(extended_tracks))
		else:
			self.error(404)

class ApiTracksDeleteHandler(BaseHandler):
	@login_required
	def delete(self, id):
		track = Track.get_by_id(int(id))

		if(track):
			#Deleting associated favorites
			task = Task(
					method = 'DELETE',
					url = "/taskqueue/deletetrack",
					params = {
						"track_id": id,
						"type": "broadcast",
					},
				)
			task.add(queue_name="worker-queue")

			response = True
		else:
			response = False

		self.response.out.write(json.dumps({ "response": response }))
