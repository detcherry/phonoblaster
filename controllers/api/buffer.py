import logging
import re
import django_setup
from django.utils import simplejson as json

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi
from models.db.station import Station

class ApiBufferHandler(BaseHandler):
	def get(self, shortname):
		#return buffer and timestamp of station
		logging.info("in get ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

		
		if(station_proxy.station):
			buffer = station_proxy.buffer_and_timestamp['buffer']
			timestamp = station_proxy.buffer_and_timestamp['timestamp']
			extended_buffer = Station.get_extended_buffer(buffer)

			bufferJSON = []

			logging.info(extended_buffer)
			logging.info(timestamp)

			buffer_and_timestamp = {'buffer':extended_buffer, 'timestamp': timestamp.isoformat()}

			self.response.out.write(json.dumps(buffer_and_timestamp))

		else:
			self.error(404)

	@login_required
	def put(self, shortname):
		#put new track in buffer
		logging.info("in put ApiBufferHandler")
		logging.info(shortname)

		youtube_tracks = (self.request.get('tracks'))
		logging.info(youtube_tracks)

		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			station_proxy.add_tracks_to_buffer(youtube_tracks)

			self.response.out.write(json.dumps({'response':True}))

		else:
			self.error(404)
		

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