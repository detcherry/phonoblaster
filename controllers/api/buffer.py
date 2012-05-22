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
		# Getting station shortname and initializing station proxy
		shortname = self.request.get('shortname')
		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			buffer = station_proxy.buffer_and_timestamp['buffer']
			timestamp = station_proxy.buffer_and_timestamp['timestamp']

			# Conveerting timestamp (stored as UTC time) to isoformat before sending JSON
			buffer_and_timestamp = {'buffer':buffer, 'timestamp': timestamp.isoformat()}
			self.response.out.write(json.dumps(buffer_and_timestamp))

		else:
			self.error(404)

	@login_required
	def post(self):
		# getting station shortname, youtube_tracks to add and initializing station proxy
		shortname = self.request.get('shortname')
		youtube_tracks = json.loads(self.request.get('tracks'))
		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			added_tracks, rejected_tracks = station_proxy.add_tracks_to_buffer(youtube_tracks)

			# Add a taskqueue to warn everyone
			data = {
				"entity": "buffer",
				"event": "add",
				"content": added_tracks,
			}

			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(data)
				}
			)
			task.add(queue_name="buffer-queue")

			self.response.out.write(json.dumps({'response':True, 'message': 'Tracks added to buffer, in the limits of the buffer. Listeners were notified.', 'rejected_tracks': rejected_tracks}))

		else:
			self.error(404)


class ApiBufferDeleteHandler(BaseHandler):
	@login_required
	def delete(self, key_name):
		# Getting shortname from key_name, which is the ID of the track to delete from buffer. Then initializing station proxy
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		response = {}

		if(station_proxy.station):
			notify_listeners = False # We'll need to tell everyone if there is a change, but not in every case

			if len(station_proxy.buffer_and_timestamp['buffer']) == 1:
				# Only one track left in the buffer
				response = {'response':False, 'message': 'You cannot delete this track because it is the last one in the buffer and a buffer cannot be empty.'}
			else:
				# More than one track left in the buffer
				result = station_proxy.remove_track_from_buffer(key_name)

				if result[0] :
					response = {'response':True, 'message':"Track with id = "+key_name+" deleted successfully!."}
					notify_listeners = True

				elif result[1]:
					# The current track is the one beeing deleted, need to start a task and delete the track after the end of the track
					current_track = station_proxy.get_current_track()
					countdown = current_track[1]["youtube_duration"] - current_track[2]
					response = {'response':False, 'message':"Track with id = "+key_name+" will be deleted in : "+str(countdown)+" s, because it is currenlty playing."}
					task = Task(
						url = "/taskqueue/buffer/delete",
						params = {
							"station": shortname,
							"id": key_name,
						},
						countdown = countdown,
					)
					task.add(queue_name="worker-queue")
					notify_listeners = True
				else:
					response = {'response':False, 'message':"Track with id = "+key_name+" not found."}

			if notify_listeners:
				# Add a taskqueue to warn everyone
				data = {
					"entity": "buffer",
					"event": "remove",
					"content": key_name,
				}

				task = Task(
					url = "/taskqueue/multicast",
					params = {
						"station": config.VERSION + "-" + shortname,
						"data": json.dumps(data)
					}
				)
				task.add(queue_name="buffer-queue")
		else:
			response = {'response':False, 'message':"Station with shortname = "+shortname+" not found."}


		self.response.out.write(json.dumps(response))