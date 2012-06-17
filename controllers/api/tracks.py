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
	def delete(self, shortname, id):
		track = Track.get_by_id(int(id))
		logging.info("Getting from datastore track with track_id = "+id+" for station : @"+shortname)
		response = True

		if(track):
			# Station Proxy
			station_proxy = StationApi(shortname)
			# Deleting associated broadcasts and favorites
			broadcasts_in_buffer = db.get(station_proxy.station.broadcasts)

			# If track associated to broadcast in buffer, track will not be deleted.
			# If not, a task queue will start to delete broadcast, favorites and the actual track
			for b in broadcasts_in_buffer:
				if b.track.key().id() == int(id):
					logging.info("Track is being broadcat, will not proceed to deletion.")
					response = False
					break

			if response:
				logging.info("Strating taskqueue to delete broadcats and likes associated to track.")
				task = Task(
						method = 'DELETE',
						url = "/taskqueue/deletetrack",
						params = {
							"track_id": id,
							"station_key_name": station_proxy.station.key().name(),
							"type": "broadcast",
						},
					)
				task.add(queue_name="worker-queue")

		else:
			response = False

		self.response.out.write(json.dumps({ "response": response }))
