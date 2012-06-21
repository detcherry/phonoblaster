import math
import logging
import re
import json

from datetime import datetime
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
			broadcasts = station_proxy.buffer['broadcasts'][:]
			timestamp = station_proxy.buffer['timestamp']

			# Converting timestamp (stored as UTC time) to UNIX milliseconds before sending JSON
			buffer = {
				'broadcasts': broadcasts, 
				'timestamp': timegm(timestamp.utctimetuple()),
			}
			self.response.out.write(json.dumps(buffer))

		else:
			self.error(404)

	@login_required
	def post(self):
		# getting station shortname, youtube_tracks to add and initializing station proxy
		shortname = self.request.get('shortname')
		content = json.loads(self.request.get("content"))				
		position = self.request.get('position')

		station_proxy = StationApi(shortname)
		data = None

		if(station_proxy.station):
			key_name = station_proxy.station.key().name()
			
			if(self.user_proxy.is_admin_of(str(key_name))):
				logging.info("User is admin of the station. Authorized to make changes to the buffer.")
				
				if position is '':
					# Adding tracks to buffer
					extended_broadcast = station_proxy.add_track_to_buffer(content)

					if not extended_broadcast:
						response = {
							'response': False,
							'error': 1, 
							'message': 'Buffer full or track not found.'
						}
					else:
						response = {
							'response': True,
							'message': 'Track successfully added to buffer.'
						}

						now = datetime.utcnow()
						data = {
							"entity": "buffer",
							"event": "new",
							"content": {
								"item": extended_broadcast,
								"created": timegm(now.utctimetuple())*1000 + math.floor(now.microsecond/1000),
							}
						}

				else:
					# Changing broadcast position in buffer
					extended_broadcast = station_proxy.move_track_in_buffer(content, int(position))

					if extended_broadcast:
						response = {
							'response': True, 
							'message': 'Track with key_name : '+ content + ' is now at : ' + position
						}

						now = datetime.utcnow()
						data = {
							"entity": "buffer",
							"event": "new",
							"content": {
								'id': content,
								'position': int(position),
								"created": timegm(now.utctimetuple())*1000 + math.floor(now.microsecond/1000),
							},
						}
					else:
						response = {
							'response':False,
							'error': 0, 
							'message': 'Error while changing position (at '+ position +') of incomming track with key_name = '+ content
						}

				# Add a taskqueue to warn everyone
				if data:
					task = Task(
						url = "/taskqueue/multicast",
						params = {
							"station": config.VERSION + "-" + shortname,
							"data": json.dumps(data)
							}
					)
					task.add(queue_name="buffer-queue")
				
			else:
				logging.info("User is not admin. Not authorized to make a change to the buffer")
				self.error(403)
				
		else:
			logging.info("Station not found. Not possible to make a change to the buffer")
			self.error(404)

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
			broadcasts = station_proxy.buffer['broadcasts'][::]
			
			if len(broadcasts) < 2:
				response = {'response': False, 'error':0, 'message': 'A buffer cannot be empty.'}
			else :
				# Deleting track
				deletion_result, result_key_name = station_proxy.remove_track_from_buffer(key_name)

				if not deletion_result:
					# The deletion was not successful
					
					if result_key_name:
						# Track client id corresponds to the currently played track
						response = {'response': False, 'error':1, 'message': 'You cannot delete the currently played track.'}
					else:
						# Track client id does not appear in the buffer
						response = {'response': False, 'error':2, 'message': 'Track with id : '+key_name+' not found!'}
				else:
					# Deletion OK
					response = {'response': True, 'message': 'Deletion of track successful'}

					# Add a taskqueue to warn everyone
					now = datetime.utcnow()
					data = {
						"entity": "buffer",
						"event": "remove",
						"content": {
							"id": key_name,
							"created": timegm(now.utctimetuple())*1000 + math.floor(now.microsecond/1000),
						}
					}

					task = Task(
						url = "/taskqueue/multicast",
						params = {
							"station": config.VERSION + "-" + shortname,
							"data": json.dumps(data),
						},
					)
					task.add(queue_name="buffer-queue")
		else:
			response = {'response':False, error:'-1', 'message': 'Station with shortname : '+shortname+' not found.'}

		self.response.out.write(json.dumps(response))