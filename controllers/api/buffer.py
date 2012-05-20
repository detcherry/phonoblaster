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
	@login_required
	def get(self):
		shortname = self.request.get('shortname')
		#return buffer and timestamp of station
		logging.info("in get ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

		
		if(station_proxy.station):
			buffer = station_proxy.buffer_and_timestamp['buffer']
			timestamp = station_proxy.buffer_and_timestamp['timestamp']

			logging.info(buffer)
			logging.info(timestamp)

			buffer_and_timestamp = {'buffer':buffer, 'timestamp': timestamp.isoformat()}

			self.response.out.write(json.dumps(buffer_and_timestamp))

		else:
			self.error(404)

	@login_required
	def post(self):
		shortname = self.request.get('shortname')
		#put new track in buffer
		logging.info("in put ApiBufferHandler")
		logging.info(shortname)

		youtube_tracks = json.loads(self.request.get('tracks'))
		logging.info(youtube_tracks)

		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			station_proxy.add_tracks_to_buffer(youtube_tracks)

			self.response.out.write(json.dumps({'response':True}))

		else:
			self.error(404)


class ApiBufferDeleteHandler(BaseHandler):
	@login_required
	def delete(self, key_name):
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)

		#delete track from buffer at position track_position
		logging.info("in delete ApiBufferHandler")
		logging.info(shortname)

		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			result = station_proxy.remove_track_from_buffer(key_name)
			if result[0] :
				self.response.out.write(json.dumps({'response':True, 'message':"Track with id = "+key_name+" deleted successfully!."}))
			elif result[1]:
				current_track = station_proxy.get_current_track()
				countdown = current_track[1]["youtube_duration"] - current_track[2]
				self.response.out.write(json.dumps({'response':False, 'message':"Track with id = "+key_name+" will be deleted in : "+str(countdown)+" s, because it is currenlty playing."}))
				task = Task(
					url = "/taskqueue/buffer/delete",
					params = {
						"station": shortname,
						"id": key_name,
					},
					countdown = countdown,
				)
				task.add(queue_name="worker-queue")
				pass
			else:
				self.response.out.write(json.dumps({'response':False, 'message':"Track with id = "+key_name+" not found."}))
		else:
			self.response.out.write(json.dumps({'response':False, 'message':"Station with shortname = "+shortname+" not found."}))