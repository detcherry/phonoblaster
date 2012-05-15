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
	def get(self, key_name):
		#return buffer and timestamp of station
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)

		logging.info("in ApiQueueDeleteHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

		
		if(station_proxy.station):
			buffer, timestamp = station_proxy.buffer_and_timestamp
			bufferJSON = []

			if buffer:
				for track in tracks:
					bufferJSON.append({
							'id': track.youtube_id,
							'title': track.youtube_title,
							'duration': track.youtube_duration,
						})

				self.response.out.write(json.dumps(bufferJSON))
		else:
			self.error(404)

		

	@login_required
	def put(self, key_name):
		#put new track in buffer
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)

		logging.info("in ApiQueueDeleteHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)
		

	@login_required
	def post(self, key_name):
		#change position of a track from old_position to new position
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)

		logging.info("in ApiQueueDeleteHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

	@login_required
	def delete(self, key_name):
		#delete track from buffer at position track_position
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)

		logging.info("in ApiQueueDeleteHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)