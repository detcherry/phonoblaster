import logging
import os
import re

from datetime import datetime
from datetime import timedelta
from calendar import timegm

from google.appengine.ext import db
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.api import memcache
from google.appengine.api.taskqueue import Task

from controllers import config

from models.db.like import Like
from models.db.station import Station
from models.db.session import Session
from models.db.broadcast import Broadcast
from models.db.track import Track
from models.db.counter import Shard

from models.api.user import UserApi
from models.api.admin import AdminApi

MEMCACHE_STATION_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".station."
MEMCACHE_STATION_SESSIONS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".sessions.station."
MEMCACHE_STATION_TRACKS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".tracks.station."
MEMCACHE_STATION_BUFFER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".buffer.station."
MEMCACHE_STATION_LIKES_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".likes.station."
COUNTER_OF_VISITS_PREFIX = "station.visits.counter."
COUNTER_OF_LIKES = "station.likes.counter."

class StationApi():
	
	def __init__(self, shortname):
		self._shortname = shortname
		self._memcache_station_id = MEMCACHE_STATION_PREFIX + self._shortname
		self._memcache_station_sessions_id = MEMCACHE_STATION_SESSIONS_PREFIX + self._shortname
		self._memcache_station_tracks_id = MEMCACHE_STATION_TRACKS_PREFIX + self._shortname
		self._memcache_station_buffer_id = MEMCACHE_STATION_BUFFER_PREFIX + self._shortname
		self._memcache_station_likes_id = MEMCACHE_STATION_LIKES_PREFIX + self._shortname
		self._counter_of_visits_id = COUNTER_OF_VISITS_PREFIX + self._shortname
		self._counter_of_likes_id = COUNTER_OF_LIKES + self._shortname
	
	# Return the station
	@property
	def station(self):
		if not hasattr(self, "_station"):
			self._station = memcache.get(self._memcache_station_id)
			if self._station is None:
				logging.info("Station not in memcache")
				self._station = Station.all().filter("shortname", self._shortname).get()
				if(self._station):
					logging.info("Station exists")
					memcache.set(self._memcache_station_id, self._station)
					logging.info("Station put in memcache")
				else:
					logging.info("Station does not exist")
			else:
				logging.info("Station already in memcache")	
		return self._station
	
	def put_station(self, id, shortname, name, link, type, full, thumb):
		station = Station(
			key_name = id,
			shortname = shortname,
			name = name,
			link = link,
			type = type,
			full = full,
			thumb = thumb,
			online = False,
			active = datetime.utcnow(),
		)
		station.put()
		logging.info("Station put in datastore")
		
		memcache.set(self._memcache_station_id, station)
		logging.info("Station put in memcache")
		
		# Put station in proxy
		self._station = station
		
		# Increment admin counter of stations
		admin_proxy = AdminApi()
		admin_proxy.increment_stations_counter()
		logging.info("Counter of stations incremented")
		
		# Mail admins
		self.mail()
		
	def mail(self):
		admin_proxy = AdminApi()
		
		subject = "New phonoblaster station: %s" % (self.station.name)
		if self.station.type == 'page':
			body = """
	A new station (%s/%s) has been created on Phonoblaster:
	%s, %s
			
	Global number of stations: %s
			""" %(config.SITE_URL, self.station.shortname, self.station.name, self.station.link, admin_proxy.number_of_stations)
		else:
			body = """
	A new station (%s/%s) has been created on Phonoblaster:
	%s, %s
			
	Global number of stations: %s
			""" %(config.SITE_URL, self.station.shortname, self.station.name, "https://graph.facebook.com/"+self.station.key().name(), admin_proxy.number_of_stations)
		
		logging.info(body)
		task = Task(
			url = "/taskqueue/mail",
			params = {
				"to": "activity@phonoblaster.com",
				"subject": subject,
				"body": body,
			}
		)
		task.add(queue_name = "worker-queue")
		
	def update_background(self, full, thumb):
		station = self.station
		
		old_full_blob_key = None
		old_thumb_blob_key = None
		
		m1 = re.match(r"/picture/([^/]+)?/view", station.full)
		m2 = re.match(r"/picture/([^/]+)?/view", station.thumb)
		if m1 and m2:
			logging.info("Background is a blob")
			old_full_blob_key = m1.group(1)
			old_thumb_blob_key = m2.group(1)
		else:
			logging.info("Background is a static file")
		
		station.full = full
		station.thumb = thumb
		
		station.put()
		logging.info("Station updated in datastore")
		
		memcache.set(self._memcache_station_id, station)
		logging.info("Station updated in memcache")
		
		# Update in runtime
		self._station = station
		
		if old_full_blob_key and old_thumb_blob_key:
			old_full = BlobInfo.get(old_full_blob_key)
			old_full.delete()
			logging.info("Old full size background removed from blobstore")
		
			old_thumb = BlobInfo.get(old_thumb_blob_key)
			old_thumb.delete()
			logging.info("Old thumbnail removed from blobstore")	
		
	
	########################################################################################################################################
	#													SESSIONS
	########################################################################################################################################

	@property
	def number_of_sessions(self):
		if not hasattr(self, "_number_of_sessions"):
			self._number_of_sessions = len(self.sessions)
			
		return self._number_of_sessions
	
	# Gives all the listeners (logged in a station)
	@property
	def sessions(self):
		if not hasattr(self, "_sessions"):
			self._sessions = memcache.get(self._memcache_station_sessions_id)
			if self._sessions is None:
				logging.info("Sessions not in memcache")
				
				q = Session.all()
				q.filter("host", self.station.key())
				q.filter("ended", None)
				q.filter("created >", datetime.utcnow() - timedelta(0,7200))
				sessions = q.fetch(100)

				extended_sessions = Session.get_extended_sessions(sessions)
				memcache.set(self._memcache_station_sessions_id, extended_sessions)
				logging.info("Sessions put in memcache")
				
				self._sessions = extended_sessions
			else:
				logging.info("Sessions already in memcache")
		
		return self._sessions
	
	def add_to_sessions(self, channel_id):
		# Get session
		session = Session.get_by_key_name(channel_id)
		extended_session = None
		
		if(session):	
			# After a reconnection the session may have ended. Correct it.
			if session.ended is not None:
				session.ended = None
				session.put()
				logging.info("Session had ended (probable reconnection). Corrected session put.")
	
			# Init listener
			listener = session.listener
			
			# Init extended session
			extended_session = Session.get_extended_session(session, listener)
	
			new_sessions = self.sessions
			new_sessions.append(extended_session)
			memcache.set(self._memcache_station_sessions_id, new_sessions)
			logging.info("Session added in memcache")
			
			# Online status becomes true if listener = host
			if(listener and listener.key().name() == Session.host.get_value_for_datastore(session).name()):
				logging.info("Admin joins")	
				
				self.station.online = True
				self.station.active = datetime.utcnow()
				self.station.put()
				logging.info("Station updated in datastore")
				
				memcache.set(self._memcache_station_id, self.station)
				logging.info("Station updated in memcache")
			
		return extended_session
	
	def remove_from_sessions(self, channel_id):
		# Get session
		session = Session.get_by_key_name(channel_id)
		extended_session = None
		
		if(session):
			session.ended = datetime.utcnow()
			session.put()
			logging.info("Session ended in datastore")
		
			# Init listener
			listener = session.listener

			# Init extended session
			extended_session = Session.get_extended_session(session, listener)
		
			new_sessions = []
			for s in self.sessions:
				if s["key_name"] != channel_id:
					new_sessions.append(s)
		
			memcache.set(self._memcache_station_sessions_id, new_sessions)
			logging.info("Session removed from memcache")
			
			# Online status becomes false if listener = host + no other host listening
			if(listener and listener.key().name() == Session.host.get_value_for_datastore(session).name()):
				logging.info("Admin leaves")
				
				still_some_admins = False
				for s in new_sessions:
					if(s["listener_key_name"] == str(listener.key().name())):
						still_some_admins = True
						break
				
				if not still_some_admins:
					self.station.online = False
					self.station.put()
					logging.info("Station updated in datastore")
										
					memcache.set(self._memcache_station_id, self.station)
					logging.info("Station updated in memcache")
				else:
					logging.info("Still some admins online")
				
		return extended_session

	########################################################################################################################################
	#													BUFFER
	########################################################################################################################################
	# Returns the current buffer of the station
	@property
	def buffer(self):
		if not hasattr(self, "_buffer"):
			self._buffer = memcache.get(self._memcache_station_buffer_id)
			if self._buffer is None:
				station = self.station
				
				if station is not None and station.broadcasts is not None:
					keys = station.broadcasts
			 		broadcasts_entities = db.get(keys)
			 		broadcasts = Broadcast.get_extended_broadcasts(broadcasts_entities, self.station)
				else:
					broadcasts = []
				
				timestamp = self.station.timestamp

				self._buffer = {
					'broadcasts': broadcasts,
					'timestamp': timestamp
				}
				
				memcache.add(self._memcache_station_buffer_id, self._buffer)
				logging.info("Buffer put in memcache")
			else:
				logging.info("Buffer retrieved from memcache")
		
		return self._buffer

	def reorder_buffer(self,buffer):
		# Getting live track
		broadcasts = buffer['broadcasts'][::] # Copy the array
		timestamp = buffer['timestamp']

		now = datetime.utcnow()

		updated_buffer = {
			"broadcasts": [],
			"timestamp": now,
		}

		elapsed = 0
		new_live_item = None
		start = 0

		buffer_duration = self.get_buffer_duration() # Relatively to old_buffer

		if buffer_duration > 0:
			offset = (timegm(now.utctimetuple()) - timegm(timestamp.utctimetuple())) % buffer_duration

			for i in xrange(0,len(broadcasts)):
				item = broadcasts[i]
				duration = item['duration']
				# This is the current broadcast
				if elapsed + duration > offset :
					start = offset - elapsed
					previous_items = broadcasts[:i]
					new_live_item = broadcasts[i]
					next_items = broadcasts[i+1:]

					updated_buffer['broadcasts'] = [new_live_item]
					updated_buffer['broadcasts'].extend(next_items)
					updated_buffer['broadcasts'].extend(previous_items)
					updated_buffer['timestamp'] = now - timedelta(0,start)
					logging.info("Buffer reordered")
					break
				# We must keep browsing the list before finding the current track
				else:
					elapsed += duration
		else:
			logging.info("Buffer is empty")

		return updated_buffer

	def put_buffer(self, buffer):
		station = self.station
		new_timestamp = buffer['timestamp']
		new_broadcasts = buffer['broadcasts']

		#Retrieving broadcasts from datastore
		key_names = []
		for i in xrange(0,len(new_broadcasts)):
			b = new_broadcasts[i]
			key_names.append(b['key_name'])

		broadcasts = Broadcast.get_by_key_name(key_names)
		b_keys = []

		for i in xrange(0,len(broadcasts)):
			b_key = broadcasts[i]
			b_keys.append(b_key.key())

		station.timestamp = new_timestamp
		station.broadcasts = b_keys
		station.active = datetime.utcnow()
		station.put()
		logging.info("Buffer put in datastore")

		self._buffer = {
			'broadcasts':new_broadcasts,
			'timestamp': new_timestamp
		}
		memcache.set(self._memcache_station_id, station)
		logging.info("Station updated in memcache")
		
		memcache.set(self._memcache_station_buffer_id, self._buffer)
		logging.info("Buffer updated in memcache")

	def get_buffer_duration(self):
		"""
			Returns the length in seconds of the buffer.
		"""
		broadcasts = self.buffer['broadcasts'][:]
		buffer_duration = 0

		if broadcasts:
			buffer_duration = sum([t['duration'] for t in broadcasts])

		return buffer_duration

	def add_track_to_buffer(self,incoming_track):
		buffer = self.reorder_buffer(self.buffer)
		new_broadcasts = buffer['broadcasts'][::]  # Copy array and resting broadcasts
		timestamp = buffer['timestamp']
		room = self.room_in_buffer()

		# Edge Case, if adding track to position 1 5 seconds before the live track ends, we reject the operation.
		# This is due to the latency of Pubnub.
		if(len(new_broadcasts) == 1):
			# We need to check if the live track ends in the next 5 seconds
			live_broadcast = new_broadcasts[0]
			live_broadcast_duration = live_broadcast['duration']
			start = timegm(datetime.utcnow().utctimetuple()) - timegm(timestamp.utctimetuple())
			time_before_end = live_broadcast_duration-start

			if(time_before_end< 5):
				# Rejecting action
				logging.info("Rejecting operation because of an edge case (adding)")
				return None
		# End of edge case
		
		extended_broadcast = None
		if(room > 0):
			logging.info("Room in buffer")
			track = Track.get_or_insert(incoming_track, self.station)

			if track:
				logging.info("Track found")

				submitter_key = None
				if(incoming_track["track_submitter_key_name"] != self.station.key().name()):
					submitter_key_name = incoming_track["track_submitter_key_name"]
					submitter_key = db.Key.from_path("Station", submitter_key_name)

				if(track.youtube_id):		
					new_broadcast = Broadcast(
						key_name = incoming_track["key_name"],
						track = track.key(),
						youtube_id = track.youtube_id,
						youtube_title = track.youtube_title,
						youtube_duration = track.youtube_duration,
						station = self.station.key(),
						submitter = submitter_key,
					)
				else:
					new_broadcast = Broadcast(
						key_name = incoming_track["key_name"],
						track = track.key(),
						soundcloud_id = track.soundcloud_id,
						soundcloud_title = track.soundcloud_title,
						soundcloud_duration = track.soundcloud_duration,
						soundcloud_thumbnail = track.soundcloud_thumbnail,
						station = self.station.key(),
						submitter = submitter_key,
					)
				
				new_broadcast.put()
				logging.info("New broadcast put in datastore")

				extended_broadcast = Broadcast.get_extended_broadcasts([new_broadcast], self.station)[0]

				# Injecting traks in buffer
				new_broadcasts.append(extended_broadcast)
				new_buffer = {
					'broadcasts': new_broadcasts,
					'timestamp': timestamp
				}

				# Save data
				self.put_buffer(new_buffer)
			else:
				logging.info("Track not found")
		else:
			logging.info("There is no more room in the buffer.")
				
		return extended_broadcast


	def remove_track_from_buffer(self,key_name):
		"""
			key_name is the id of the track in the buffer that has to be removed. This methods returns a tuple, the first argument i a boolean,
			it tells if the remove was successfull, the second argument is an integer or None.

			If the remove was successfull : (True, key_name).
			If key_name does not correspond to anny track, this method returns (False, None).
			If key_name is OK but represents the track that is being played : (False, key_name)

		"""
		
		buffer = self.reorder_buffer(self.buffer)
		broadcasts = buffer['broadcasts'][::] # Copy array and resting broadcasts
		timestamp = buffer['timestamp']
		index_broadcast_to_find = None

		# Retrieving index corresponding to id
		for i in xrange(0,len(broadcasts)):
			broadcast = broadcasts[i]
			if broadcast['key_name'] == key_name:
				index_broadcast_to_find = i
				break

		# Edge Case, if remove track at position 1 just 5 seconds before the live track ends, we reject the operation.
		# This is due to the latency of Pubnub.
		if index_broadcast_to_find == 1:
			# We need to check if the live track ends in the next 5 seconds
			live_broadcast = broadcasts[0]
			live_broadcast_duration = live_broadcast['duration']
			start = timegm(datetime.utcnow().utctimetuple()) - timegm(timestamp.utctimetuple())
			time_before_end = live_broadcast_duration-start

			if time_before_end< 5:
				# Rejecting action
				logging.info("Rejecting operation because of edge case (deletion)")
				return False
		# End of edge case

		if index_broadcast_to_find is not None:
			live_broadcast = broadcasts[0]
			live_broadcast_key_name = live_broadcast['key_name']

			if live_broadcast_key_name != key_name:
				# index retrieved and not corresponding to the current played track
				logging.info("Broadcast with key_name="+key_name+" found. Not the live track. Deletion authorized.")
				broadcasts.pop(index_broadcast_to_find)
				new_buffer = {
					'broadcasts':broadcasts,
					'timestamp':timestamp
				}
				# Saving data
				self.put_buffer(new_buffer)
				return True
			else:
				# index retrived and corresponding to the currently plyayed track
				logging.info("Broadcast with key_name="+key_name+" found. Is the live track. Deletion not authorized.")
				return False
		else:
			# index not retrieved, the id is not valid
			logging.info("Broadcast with key_name="+key_name+" not found. Deletion not possible")
			return False

	def move_track_in_buffer(self,key_name, position):
		"""
			Moving track with key_name to new position.
		"""
		buffer = self.reorder_buffer(self.buffer)
		broadcasts = buffer['broadcasts'][::] # Copy the array
		timestamp = buffer['timestamp']
		extended_broadcast = None

		if(len(buffer) == 0):
			logging.info("Buffer is empty.")
			return None

		# Edge Case, if moving track to position 1 5 seconds before the live track ends, we reject the operation.
		# This is due to the latency of Pubnub.
		if(position == 1):
			# We need to check if the live track ends in the next 5 seconds
			live_broadcast = broadcasts[0]
			live_broadcast_duration = live_broadcast['duration']
			start = timegm(datetime.utcnow().utctimetuple()) - timegm(timestamp.utctimetuple())
			time_before_end = live_broadcast_duration-start

			if(time_before_end< 5):
				# Rejecting action
				logging.info("Rejecting operation because of an edge case (moving)")
				return None
		# End of edge case

		if(position>=0 and position<len(broadcasts)):
			live_broadcast = broadcasts[0]
			if not ( 0 == position or live_broadcast['key_name'] == key_name):
				# Looking for index of track to change position:

				index_track_to_move = None

				for i in xrange(0,len(broadcasts)):
					if broadcasts[i]['key_name'] == key_name:
						index_track_to_move = i
						break

				if index_track_to_move:
					broadcasts.insert(position, broadcasts.pop(index_track_to_move))
					extended_broadcast = broadcasts[position]
					logging.info("Inserting track with key_name = "+ key_name +" at position :"+str(position))
					
					# Saving data
					new_buffer = {
						'broadcasts': broadcasts,
						'timestamp': timestamp
					}
					self.put_buffer(new_buffer)
				else:
					logging.info("Track with key_name = "+key_name+" was not found, impossible to proceed to insertion.")

			else:
				logging.info("Track with key_name = "+key_name+" is the currently broadcast track, or is inserting at position 0, inserting is cacelled")

		else:
			logging.info("In StationApi.move_track_in_buffer, position is not in the range [0,"+str(len(broadcasts))+"[")

		return extended_broadcast

	# Returns the room in the queue
	def room_in_buffer(self):
		return(30 - len(self.buffer['broadcasts']))

	########################################################################################################################################
	#													VISITS
	########################################################################################################################################

	# Visits counter
	@property
	def number_of_visits(self):
		if not hasattr(self, "_number_of_visits"):
			shard_name = self._counter_of_visits_id
			self._number_of_visits = Shard.get_count(shard_name)
		return self._number_of_visits
	
	def increment_visits_counter(self):
		shard_name = self._counter_of_visits_id
		Shard.task(shard_name, "increment")
		
	########################################################################################################################################
	#													TRACKS
	########################################################################################################################################

	def get_tracks(self, offset):
		tracks = self.tracks_query(offset)
		extended_tracks = Track.get_extended_tracks(tracks)
				
		return extended_tracks
	
	
	def tracks_query(self, offset):		
		q = Track.all()
		q.filter("station", self.station.key())
		q.filter("created <", offset)
		q.order("-created")
		tracks = q.fetch(10)
		
		return tracks

	########################################################################################################################################
	#													LIKES
	########################################################################################################################################
	
	def get_likes(self, offset):
		likes = self.likes_query(offset)
		extended_likes = Like.get_extended_likes(likes)
			
		return extended_likes
	
	def likes_query(self, offset):
		q = Like.all()
		q.filter("listener", self.station)
		q.filter("created <", offset)
		q.order("-created")
		likes = q.fetch(10)
		
		return likes

	def add_to_likes(self, track):
		# Check if the like hasn't been stored yet
		q = Like.all()
		q.filter("listener", self.station.key())
		q.filter("track", track.key())
		existing_like = q.get()
		
		if(existing_like):
			logging.info("Track already liked by this listener")
		else:
			like = Like(
				track = track.key(),
				listener = self.station.key(),
			)
			like.put()
			logging.info("Like saved into datastore")
	
			self.increment_likes_counter()
			logging.info("Listener likes counter incremented")
			
			Track.increment_likes_counter(track.key().id())
			logging.info("Track likes counter incremented")

	def delete_from_likes(self, track):
		q = Like.all()
		q.filter("listener", self.station.key())
		q.filter("track", track.key()) 
		like = q.get()
				
		if like is None:
			logging.info("This track has never been liked by this listener")
		else:
			like.delete()
			logging.info("Like deleted from datastore")
			
			self.decrement_likes_counter()
			logging.info("Listener Likes counter decremented")
			
			Track.decrement_likes_counter(track.key().id())
			logging.info("Track likes counter decremented")
	
	@property
	def number_of_likes(self):
		if not hasattr(self, "_number_of_likes"):
			shard_name = self._counter_of_likes_id
			self._number_of_likes = Shard.get_count(shard_name)
		return self._number_of_likes
	
	def increment_likes_counter(self):
		shard_name = self._counter_of_likes_id
		Shard.task(shard_name, "increment")

	def decrement_likes_counter(self):
		shard_name = self._counter_of_likes_id
		Shard.task(shard_name, "decrement")
		