import logging
import os
import re

from datetime import datetime
from datetime import timedelta
from calendar import timegm

from google.appengine.ext import db
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
MEMCACHE_STATION_QUEUE_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".queue.station."
MEMCACHE_STATION_SESSIONS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".sessions.station."
MEMCACHE_STATION_BROADCASTS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".broadcasts.station."
MEMCACHE_STATION_TRACKS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".tracks.station."
MEMCACHE_STATION_BUFFER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".buffer.station."
MEMCACHE_STATION_LIKES_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".likes.station."
COUNTER_OF_BROADCASTS_PREFIX = "station.broadcasts.counter."
COUNTER_OF_VIEWS_PREFIX = "station.views.counter."
COUNTER_OF_SUGGESTIONS_PREFIX = "station.suggestions.counter."
COUNTER_OF_VISITS_PREFIX = "station.visits.counter."
COUNTER_OF_LIKES = "station.likes.counter."

class StationApi():
	
	def __init__(self, shortname):
		self._shortname = shortname
		self._memcache_station_id = MEMCACHE_STATION_PREFIX + self._shortname
		self._memcache_station_queue_id = MEMCACHE_STATION_QUEUE_PREFIX + self._shortname
		self._memcache_station_sessions_id = MEMCACHE_STATION_SESSIONS_PREFIX + self._shortname
		self._memcache_station_broadcasts_id = MEMCACHE_STATION_BROADCASTS_PREFIX + self._shortname
		self._memcache_station_tracks_id = MEMCACHE_STATION_TRACKS_PREFIX + self._shortname
		self._memcache_station_buffer_id = MEMCACHE_STATION_BUFFER_PREFIX + self._shortname
		self._memcache_station_likes_id = MEMCACHE_STATION_LIKES_PREFIX + self._shortname
		self._counter_of_broadcasts_id = COUNTER_OF_BROADCASTS_PREFIX + self._shortname
		self._counter_of_views_id = COUNTER_OF_VIEWS_PREFIX + self._shortname
		self._counter_of_suggestions_id = COUNTER_OF_SUGGESTIONS_PREFIX + self._shortname
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
	
	def put_station(self, id, shortname, name, link, type):
		station = Station(
			key_name = id,
			shortname = shortname,
			name = name,
			link = link,
			type = type,
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
		body = """
A new station (%s/%s) has been created on Phonoblaster:
%s, %s
		
Global number of stations: %s
		""" %(config.SITE_URL, self.station.shortname, self.station.name, self.station.link, admin_proxy.number_of_stations)
		
		task = Task(
			url = "/taskqueue/mail",
			params = {
				"to": "activity@phonoblaster.com",
				"subject": subject,
				"body": body,
			}
		)
		task.add(queue_name = "worker-queue")
	
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
		# After a reconnection the session may have ended. Correct it.
		if session.ended is not None:
			session.ended = None
			session.put()
			logging.info("Session had ended (probable reconnection). Corrected session put.")
		
		# Init listener
		listener = session.listener

		extended_session = Session.get_extended_session(session, listener)
		
		new_sessions = self.sessions
		new_sessions.append(extended_session)
		memcache.set(self._memcache_station_sessions_id, new_sessions)
		logging.info("Session added in memcache")
			
		return extended_session
	
	def remove_from_sessions(self, channel_id):
		# Get session
		session = Session.get_by_key_name(channel_id)
		session.ended = datetime.utcnow()
		session.put()
		logging.info("Session ended in datastore")
		
		# Init listener
		listener = session.listener

		extended_session = Session.get_extended_session(session, listener)
		
		new_sessions = []
		for s in self.sessions:
			if s["key_name"] != channel_id:
				new_sessions.append(s)
		
		memcache.set(self._memcache_station_sessions_id, new_sessions)
		logging.info("Session removed from memcache")
		
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

				self._buffer = {'broadcasts':broadcasts, 'timestamp':timestamp}
				
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
				duration = item['youtube_duration']
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


		#Putting data in datastore
		station.timestamp = new_timestamp
		station.broadcasts = b_keys
		station.put()
		logging.info("Putting station with new buffer in DATASTORE")

		#Updating memcache
		self._buffer = {'broadcasts':new_broadcasts, 'timestamp': new_timestamp}
		memcache.set(self._memcache_station_id, station)
		memcache.set(self._memcache_station_buffer_id, {'broadcasts':new_broadcasts, 'timestamp': new_timestamp} )
		logging.info("Updating station and buffer in MEMCACHE")


	def get_buffer_duration(self):
		"""
			Returns the length in seconds of the buffer.
		"""
		broadcasts = self.buffer['broadcasts'][:]
		buffer_duration = 0

		if broadcasts:
			buffer_duration = sum([t['youtube_duration'] for t in broadcasts])

		return buffer_duration

	def add_track_to_buffer(self,incoming_track):
		buffer = self.reorder_buffer(self.buffer)
		new_broadcasts = buffer['broadcasts'][::]  # Copy array and resting broadcasts
		timestamp = buffer['timestamp']
		room = self.room_in_buffer()


		# Edge Case, if adding track to position 1 5 seconds before the live track ends, we reject the operation.
		# This is due to the latency of Pubnub.
		if len(new_broadcasts) == 1:
			# We need to check if the live track ends in the next 5 seconds
			live_broadcast = new_broadcasts[0]
			live_broadcast_duration = live_broadcast['youtube_duration']
			start = timegm(datetime.utcnow().utctimetuple()) - timegm(timestamp.utctimetuple())
			time_before_end = live_broadcast_duration-start

			if time_before_end< 5:
				# Rejecting action
				logging.info("Rejecting operation because of an edge case (adding)")
				return None

		# End of edge case


		extended_broadcast = None
		if room > 0 :
			logging.info("Room found in buffer.")

			track = None

			if incoming_track["track_id"]:
				track = Track.get_by_id(int(incoming_track["track_id"]))
			else:
				if(incoming_track["youtube_id"]):
					track = Track.get_or_insert_by_youtube_id(incoming_track, self.station)

			if track:
				logging.info("Track found")

				submitter_key = None

				if(incoming_track["type"] == "suggestion"):
					submitter_key_name = incoming_track["track_submitter_key_name"]
					submitter_key = db.Key.from_path("Station", submitter_key_name)

				new_broadcast = Broadcast(
					key_name = incoming_track["key_name"],
					track = track.key(),
					station = self.station.key(),
					submitter = submitter_key,
				)

				new_broadcast.put()
				logging.info("New broadcast put in datastore")

				extended_broadcast = Track.get_extended_track(track)

				# Suggested broadcast
				if(submitter_key):
					logging.info("Suggested Broadcast")

					submitter = db.get(submitter_key)
					extended_broadcast["track_submitter_key_name"] = submitter.key().name()
					extended_broadcast["track_submitter_name"] = submitter.name
					extended_broadcast["track_submitter_url"] = "/" + submitter.shortname
					extended_broadcast["type"] = "rebroadcast"
				else:
					station_key = Track.station.get_value_for_datastore(track)	
					
					# Regular broadcast
					if(station_key == self.station.key()):
						logging.info("Regular Broadcast")
						station = self.station
						extended_broadcast["type"] = "track"
					# Rebroadcast
					else:
						logging.info("Regular Broadcast")
						station = db.get(station_key)
						extended_broadcast["type"] = "rebroadcast"

					extended_broadcast["track_submitter_key_name"] = station.key().name()
					extended_broadcast["track_submitter_name"] = station.name
					extended_broadcast["track_submitter_url"] = "/" + station.shortname

				extended_broadcast['key_name'] = incoming_track['key_name']

				# Injecting traks in buffer
				new_broadcasts.append(extended_broadcast)


				new_buffer = {'broadcasts':new_broadcasts, 'timestamp':timestamp}

				#Saving data
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

		# Edge Case, if remove track at position 1 5 seconds before the live track ends, we reject the operation.
		# This is due to the latency of Pubnub.
		if index_broadcast_to_find == 1:
			# We need to check if the live track ends in the next 5 seconds
			live_broadcast = broadcasts[0]
			live_broadcast_duration = live_broadcast['youtube_duration']
			start = timegm(datetime.utcnow().utctimetuple()) - timegm(timestamp.utctimetuple())
			time_before_end = live_broadcast_duration-start

			if time_before_end< 5:
				# Rejecting action
				logging.info("Rejecting operation because of an edge case (deletion)")
				return False, False

		# End of edge case

		if index_broadcast_to_find is not None:
			live_broadcast = broadcasts[0]
			live_broadcast_key_name = live_broadcast['key_name']

			if live_broadcast_key_name != key_name:
				# index retrieved and not corresponding to the current played track
				logging.info("Broadcast with key_name="+key_name+" found and is not the currently played track. Will proceed to deletion.")
				broadcasts.pop(index_broadcast_to_find)
				new_buffer = {'broadcasts':broadcasts, 'timestamp':timestamp}
				# Saving data
				self.put_buffer(new_buffer)
				return (True, key_name)
			else:
				# index retrived and corresponding to the currently plyayed track
				logging.info("Broadcast with key_name="+key_name+" found but is the currently played track. Will NOT proceed to deletion.")
				return (False, key_name)
		else:
			# index not retrieved, the id is not valid
			logging.info("Broadcast with key_name="+key_name+" NOT found. Will NOT proceed to deletion.")
			return (False, None)


	def move_track_in_buffer(self,key_name, position):
		"""
			Moving track with key_name to new position.
		"""
		buffer = self.reorder_buffer(self.buffer)
		broadcasts = buffer['broadcasts'][::] # Copy the array
		timestamp = buffer['timestamp']
		extended_broadcast = None

		if len(buffer) == 0:
			logging.info("Buffer is empty.")
			return None

		# Edge Case, if moving track to position 1 5 seconds before the live track ends, we reject the operation.
		# This is due to the latency of Pubnub.
		if position == 1:
			# We need to check if the live track ends in the next 5 seconds
			live_broadcast = broadcasts[0]
			live_broadcast_duration = live_broadcast['youtube_duration']
			start = timegm(datetime.utcnow().utctimetuple()) - timegm(timestamp.utctimetuple())
			time_before_end = live_broadcast_duration-start

			if time_before_end< 5:
				# Rejecting action
				logging.info("Rejecting operation because of an edge case (moving)")
				return None

		# End of edge case

		if position>=0 and position<len(broadcasts) :
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
					logging.info("Inserting track with ky_name = "+key_name+" at position :"+str(position))
					# Saving data
					new_buffer = {'broadcasts':broadcasts, 'timestamp':timestamp}
					self.put_buffer(new_buffer)
				else:
					logging.info("Track with ky_name = "+key_name+" was not found, impossible to proceed to insertion.")

			else:
				logging.info("Track with ky_name = "+key_name+" is the currently broadcast track, or is inserting at position 0, inserting is cacelled")
				

		else:
			logging.info("In StationApi.move_track_in_buffer, position is not in the range [0,"+str(len(broadcasts))+"[")

		return extended_broadcast

	# Returns the room in the queue
	def room_in_buffer(self):
		return(30 - len(self.buffer['broadcasts']))

	########################################################################################################################################
	#													END BUFFER
	########################################################################################################################################


	def task_visit(self):
		task = Task(
			url = "/taskqueue/visit",
			params = {
				"shortname": self._shortname,
			}
		)
		task.add(queue_name = "worker-queue")
	
	
	
	# Visits counter
	@property
	def number_of_visits(self):
		if not hasattr(self, "_number_of_visits"):
			shard_name = self._counter_of_visits_id
			self._number_of_visits = Shard.get_count(shard_name)
		return self._number_of_visits
	
	def increase_visits_counter(self, value):
		shard_name = self._counter_of_visits_id
		Shard.increase(shard_name, value)
	
		
	def get_tracks(self, offset):
		timestamp = timegm(offset.utctimetuple())
		memcache_tracks_id = self._memcache_station_tracks_id + "." + str(timestamp)
		
		past_tracks = memcache.get(memcache_tracks_id)
		if past_tracks is None:
			logging.info("Past tracks not in memcache")
			
			tracks = self.tracks_query(offset)
			logging.info("Past tracks retrieved from datastore")
			
			past_tracks = Track.get_extended_tracks(tracks)
			
			memcache.set(memcache_tracks_id, past_tracks)
			logging.info("Extended tracks put in memcache")
		else:
			logging.info("Past tracks already in memcache")
		
		return past_tracks
	
	def tracks_query(self, offset):		
		q = Track.all()
		q.filter("station", self.station.key())
		q.filter("created <", offset)
		q.order("-created")
		tracks = q.fetch(10)
		
		return tracks
		
	@property
	def number_of_suggestions(self):
		if not hasattr(self, "_number_of_suggestions"):
			shard_name = self._counter_of_suggestions_id
			self._number_of_suggestions = Shard.get_count(shard_name)
		return self._number_of_suggestions

	def increment_suggestions_counter(self):
		shard_name = self._counter_of_suggestions_id
		Shard.task(shard_name, "increment")

	########################################################################################################################################
	#													LIKES
	########################################################################################################################################
	def get_likes(self, offset):
		timestamp = timegm(offset.utctimetuple())
		memcache_likes_id = self._memcache_station_likes_id + "." + str(timestamp)
		
		past_likes = memcache.get(memcache_likes_id)
		if past_likes is None:
			logging.info("Past likes not in memcache")
			
			likes = self.likes_query(offset)
			logging.info("Past likes retrieved from datastore")
			
			extended_likes = Like.get_extended_likes(likes)
			past_likes = extended_likes
			
			memcache.set(memcache_likes_id, past_likes)
			logging.info("Extended likes put in memcache")
		else:
			logging.info("Likes already in memcache")
		
		return past_likes

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

	########################################################################################################################################
	#													DEPRECATED
	########################################################################################################################################

	# TO BE REMOVED
	# Check if station is on air
	def on_air(self):
		on_air = False
		if(len(self.queue) > 0):
			on_air = True
				
		return on_air
	#TO BE REMOVED AT THE END OF V4 DEV
	# Returns the current station queue
	@property
	def queue(self):
		if not hasattr(self, "_queue"):
			self._queue = memcache.get(self._memcache_station_queue_id)
			if self._queue is None:
				q = Broadcast.all()
				q.filter("station", self.station.key())
				q.filter("expired >", datetime.utcnow())
				q.order("expired")
		 		broadcasts = q.fetch(10)
	
				# Format extended broadcasts
				self._queue = Broadcast.get_extended_broadcasts(broadcasts, self.station)
	
				# Put extended broadcasts in memcache
				memcache.add(self._memcache_station_queue_id, self._queue)
				logging.info("Queue loaded in memcache")
			else:
				# We probably have to clean the memcache from old tracks
				cleaned_up_queue = []
				datetime_now = timegm(datetime.utcnow().utctimetuple())
			
				for broadcast in self._queue:
					if(broadcast["expired"] > datetime_now):
						cleaned_up_queue.append(broadcast)
			
				# We only update the memcache if some cleaning up was necessary
				if(len(self._queue) != len(cleaned_up_queue)):
					self._queue = cleaned_up_queue
					memcache.set(self._memcache_station_queue_id, self._queue)
					logging.info("Queue already in memcache and cleaned up")
				else:
					logging.info("Queue already in memcache and no need to clean up")

		return self._queue		

	#TO BE REMOVED AT THE END OF V4 DEV
	# Add a new broadcast to the queue
	def add_to_queue(self, broadcast):
		extended_broadcast = None
		if broadcast:
			room = self.room()
			if(room == 0):
				logging.info("Queue full")
			else:
				logging.info("Some room in the queue")

				track = None

				if(broadcast["track_id"]):
					track = Track.get_by_id(int(broadcast["track_id"]))
						
				else:
					# If obviously not, look for it though, save it otherwise and get extended track from Youtube
					if(broadcast["youtube_id"]):
						track = Track.get_or_insert_by_youtube_id(broadcast, self.station)

				if(track):
					logging.info("Track on Phonoblaster")

					user_key = None
					if(broadcast["type"] == "suggestion"):
						user_key_name = broadcast["track_submitter_key_name"]
						user_key = db.Key.from_path("User", user_key_name)

					# Get the queue expiration time
					queue_expiration_time = self.expiration_time()

					new_broadcast = Broadcast(
						key_name = broadcast["key_name"],
						track = track.key(),
						station = self.station.key(),
						user = user_key,
						expired = queue_expiration_time + timedelta(0, track.youtube_duration),
					)
					new_broadcast.put()
					logging.info("New broadcast put in datastore")
					
					# Suggested broadcast
					if(user_key):
						user = db.get(user_key)
						extended_broadcast = Broadcast.get_extended_broadcast(new_broadcast, track, None, user)
					else:
						station_key = Track.station.get_value_for_datastore(track)					
						
						# Regular broadcast
						if(station_key == self.station.key()):
							extended_broadcast = Broadcast.get_extended_broadcast(new_broadcast, track, self.station, None)	
						# Rebroadcast
						else:
							station = db.get(station_key)
							extended_broadcast = Broadcast.get_extended_broadcast(new_broadcast, track, station, None)											

					# Put extended broadcasts in memcache
					self._queue.append(extended_broadcast)
					memcache.set(self._memcache_station_queue_id, self._queue)
					logging.info("Queue updated in memcache")

					self.increment_broadcasts_counter()
					
					if(len(self.queue) == 1):
						logging.info("First track added in the queue")
						self.task_view()

		return extended_broadcast	
	
	# TO BE REMOVED
	# Returns the room in the queue
	def room(self):
		return(10 - len(self.queue))
	
	# TO BE REMOVED
	# Returns the station expiration time or the current time if there is no track in the tracklist
	def expiration_time(self):
		if not self.queue:
			logging.info("Queue empty")
			return datetime.utcnow()
		else:
			logging.info("Queue not empty")
			last_broadcast = self.queue[-1]
			return datetime.utcfromtimestamp(last_broadcast["expired"])
	
	# TO BE REMOVED
	def task_view(self):
		task = Task(
			url = "/taskqueue/view",
			params = {
				"shortname": self._shortname,
			}
		)
		task.add(queue_name = "worker-queue")
	
	#TO BE REMOVED AT THE END OF V4 DEV
	# Remove a broadcast from the queue
	def remove_from_queue(self, key_name):
		response = False
		logging.info("Removing from queue")
		logging.info(key_name)
		
		# If the queue has at least 2 broadcasts (given that the first one cannot be removed)
		if(len(self.queue) > 1):
			
			unchanged_extended_broadcasts = []
			live_extended_broadcast = self.queue[0]
			extended_broadcasts_to_edit = self.queue[:][1:] # Copy the array
			
			for i in xrange(len(self.queue[1:])): 
				extended_broadcast = self.queue[1:][i]
				if(extended_broadcast["key_name"] != key_name):
					# Broadcasts must be be featured in the unchanged list and be removed from the list to edit
					unchanged_extended_broadcasts.append(extended_broadcast)
					extended_broadcasts_to_edit.pop(0)
				else:
					# We have found the broadcast to remove, stop the loop
					break;
						
			# If broadcast to remove
			if(len(extended_broadcasts_to_edit) > 0):
				# Retrieve broadcasts to edit key names
				extended_broadcasts_to_edit_key_names = []
				for extended_broadcast in extended_broadcasts_to_edit:
					extended_broadcasts_to_edit_key_names.append(extended_broadcast["key_name"])
				
				# Retrieve broadcasts to edit datastore entities
				broadcasts_to_edit = Broadcast.get_by_key_name(extended_broadcasts_to_edit_key_names)
				logging.info("Broadcat to edit")
				logging.info(broadcasts_to_edit)
				# The first broadcast to edit is the broadcast to delete
				broadcast_to_delete = broadcasts_to_edit.pop(0)
				extended_broadcast_to_delete = extended_broadcasts_to_edit.pop(0)
				expiration_offset = timedelta(0, extended_broadcast_to_delete["youtube_duration"])
				extended_expiration_offset = int(extended_broadcast_to_delete["youtube_duration"])
				
				broadcast_to_delete.delete()
				logging.info("Broadcast deleted from datastore")
				
				# Edit broadcasts
				broadcasts_edited = []
				extended_broadcasts_edited = []
				if(len(broadcasts_to_edit) > 0 and len(extended_broadcasts_to_edit) > 0):
					for broadcast in broadcasts_to_edit:
						broadcast.expired -= expiration_offset
						broadcasts_edited.append(broadcast)
					
					for extended_broadcast in extended_broadcasts_to_edit:
						extended_broadcast["expired"] -= extended_expiration_offset
						extended_broadcasts_edited.append(extended_broadcast)
					
					db.put(broadcasts_edited)
					logging.info("Following broadcasts edited in datastore")
					
				self.queue =  [live_extended_broadcast] + unchanged_extended_broadcasts + extended_broadcasts_edited
				memcache.set(self._memcache_station_queue_id, self.queue)
				logging.info("Queue updated in memcache")
				
				self.decrement_broadcasts_counter()
				
				response = True
		
		return response
	
	#TO BE REMOVED AT THE END OF V4 DEV
	@property
	def number_of_broadcasts(self):
		if not hasattr(self, "_number_of_broadcasts"):
			shard_name = self._counter_of_broadcasts_id
			self._number_of_broadcasts = Shard.get_count(shard_name)
		return self._number_of_broadcasts
	
	#TO BE REMOVED AT THE END OF V4 DEV
	# Starts a task that will increment the number of broadcasts
	def increment_broadcasts_counter(self):
		shard_name = self._counter_of_broadcasts_id
		Shard.task(shard_name, "increment")
	
	#TO BE REMOVED AT THE END OF V4 DEV
	# Starts a task that will decrement the number of broadcasts
	def decrement_broadcasts_counter(self):
		shard_name = self._counter_of_broadcasts_id
		Shard.task(shard_name, "decrement")
	# TO BE REMOVED
	@property
	def number_of_views(self):
		if not hasattr(self, "_number_of_views"):
			shard_name = self._counter_of_views_id
			self._number_of_views = Shard.get_count(shard_name)
		return self._number_of_views
	
	# TO BE REMOVED
	def increase_views_counter(self, value):
		shard_name = self._counter_of_views_id
		Shard.increase(shard_name, value)
	
	#TO BE REMOVED AT THE END OF V4 DEV
	def get_broadcasts(self, offset):
		timestamp = timegm(offset.utctimetuple())
		memcache_broadcasts_id = self._memcache_station_broadcasts_id + "." + str(timestamp)
		
		past_broadcasts = memcache.get(memcache_broadcasts_id)
		if past_broadcasts is None:
			logging.info("Past broadcasts not in memcache")
			
			broadcasts = self.broadcasts_query(offset)
			logging.info("Past broadcasts retrieved from datastore")
			
			extended_broadcasts = Broadcast.get_extended_broadcasts(broadcasts, self.station)
			past_broadcasts = extended_broadcasts
			
			memcache.set(memcache_broadcasts_id, past_broadcasts)
			logging.info("Extended past broadcasts put in memcache")
			
		else:
			logging.info("Past broadcasts already in memcache")
			
		return past_broadcasts
	
	#TO BE REMOVED AT THE END OF V4 DEV
	def broadcasts_query(self, offset):
		q = Broadcast.all()
		q.filter("station", self.station.key())
		q.filter("created <", offset)
		q.order("-created")
		broadcasts = q.fetch(10)
		
		return broadcasts
		