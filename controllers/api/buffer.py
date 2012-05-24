import logging
import re
import django_setup
from django.utils import simplejson as json
from calendar import timegm

from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi
from models.db.station import Station

class ApiBufferHandler(BaseHandler):
	def get(self):
		# Getting station shortname and initializing station proxy
		shortname = self.request.get('shortname')
		station_proxy = StationApi(shortname)

		if(station_proxy.station):
			buffer = station_proxy.buffer_and_timestamp['buffer']
			timestamp = station_proxy.buffer_and_timestamp['timestamp']

			# Converting timestamp (stored as UTC time) to isoformat before sending JSON
			buffer_and_timestamp = {
				'buffer': buffer, 
				'timestamp': timegm(timestamp.utctimetuple()),
			}
			self.response.out.write(json.dumps(buffer_and_timestamp))

		else:
			self.error(404)

	@login_required
	def post(self):
		# getting station shortname, youtube_tracks to add and initializing station proxy
		shortname = self.request.get('shortname')
		youtube_tracks = json.loads(self.request.get('tracks'))
		position = self.request.get('position')

		station_proxy = StationApi(shortname)

		data = None

		if(station_proxy.station):
			# Resetting buffer
			station_proxy.reset_buffer()

			if position is '':
				# Adding tracks to buffer
				tracks_to_add, rejected_tracks = station_proxy.add_tracks_to_buffer(youtube_tracks)

				if len(rejected_tracks) > 0:
					response = {'response':False, 'error':1, 'message': 'Some tracks were rejected because a buffer cannot contain more than 30 tracks.', 'rejected_tracks':rejected_tracks}
				else:
					response = {'response': True, 'message': 'Adding tracks to buffer done successfully.'}

				if len(tracks_to_add)>0:
					data = {
						"entity": "buffer",
						"event": "add",
						"content": tracks_to_add,
					}
			else:
				# Changing track position in buffer
				changeDone, isCurrentTrack = station_proxy.move_tack_in_buffer(youtube_tracks[0]['client_id'], int(position))

				if changeDone:
					response = {'response':True, 'message': 'Track with client_id : '+youtube_tracks[0]['client_id']+' is now at : '+position}
					data = {
						"entity": "buffer",
						"event": "change",
						"content": {'track': youtube_tracks[0], 'position': int(position)},
					}
				elif isCurrentTrack:
					response = {'response':False, 'error':0, 'message': 'It is not possible to add a track at the first position of the buffer (position of the currently played track)'}

				else:
					response = {'response': False, 'error':2, 'message': 'Position not in range.'}



				# Add a taskqueue to warn everyone
				if data:
					task = Task(
						url = "/taskqueue/multicast",
						params = {
							"station": config.VERSION + "-" + shortname,
							"data": json.dumps(data),
							"server_time": timegm(station_proxy.station.updated.utctimetuple())
						}
					)
					task.add(queue_name="buffer-queue")

		else:
			response = {'response':False, error:'-1', 'message': 'Station with shortname : '+shortname+' not found.'}


		self.response.out.write(json.dumps(response))


class ApiBufferDeleteHandler(BaseHandler):
	@login_required
	def delete(self, key_name):
		# Getting shortname from key_name, which is the ID of the track to delete from buffer. Then initializing station proxy
		m = re.match(r"(\w+).(\w+).(\w+).(\w+)", key_name)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		response = {}

		if(station_proxy.station):
			# Resetting buffer
			station_proxy.reset_buffer()

			buffer = station_proxy.buffer_and_timestamp['buffer'][::]
			
			if len(buffer) < 2:
				response = {'response': False, 'error':0, 'message': 'A buffer cannot be empty.'}
			else :
				# Deleting track
				deletion_result, client_id = station_proxy.remove_track_from_buffer(key_name)

				if not deletion_result:
					# The deletion was not successful
					
					if client_id:
						# Track client id corresponds to the currently played track
						response = {'response': False, 'error':1, 'message': 'You cannot delete the currently played track.'}
					else:
						# Track client id does not appear in the buffer
						response = {'response': False, 'error':2, 'message': 'Track with id : '+key_name+' not found!'}
				else:
					# Deletion OK
					response = {'response': True, 'message': 'Deletion of track successful'}

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
							"data": json.dumps(data),
							"server_time": timegm(station_proxy.station.updated.utctimetuple())
						},
					)
					task.add(queue_name="buffer-queue")
		else:
			response = {'response':False, error:'-1', 'message': 'Station with shortname : '+shortname+' not found.'}

		self.response.out.write(json.dumps(response))