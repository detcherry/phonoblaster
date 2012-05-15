import logging
import re
import django_setup
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi

class ApiBufferHandler(BaseHandler):
	def get(self, shortname):
		#return buffer and timestamp of station
		logging.info("in get ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

		
		if(station_proxy.station):
			buffer = station_proxy.buffer_and_timestamp['buffer']
			timestamp = station_proxy.buffer_and_timestamp['timestamp']

			bufferJSON = []

			logging.info(buffer)
			logging.info(timestamp)

			for track in buffer:
				bufferJSON.append({
						'id': track.youtube_id,
						'title': track.youtube_title,
						'duration': track.youtube_duration,
					})

			buffer_and_timestamp = {'buffer':bufferJSON, 'timestamp': timestamp.isoformat()}

			self.response.out.write(json.dumps(buffer_and_timestamp))

		else:
			self.error(404)

		

	@login_required
	def put(self, shortname):
		#put new track in buffer
		logging.info("in put ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)
		

	@login_required
	def post(self, shortname):
		#change position of a track from old_position to new position
		logging.info("in post ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

	@login_required
	def delete(self, shortname):
		#delete track from buffer at position track_position
		logging.info("in delete ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)