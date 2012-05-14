import logging
import os
import re
from calendar import timegm

from datetime import datetime
from datetime import timedelta
from calendar import timegm

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.taskqueue import Task

from controllers import config

from models.db.station import Station
from models.db.session import Session
from models.db.comment import Comment
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
COUNTER_OF_BROADCASTS_PREFIX = "station.broadcasts.counter."
COUNTER_OF_VIEWS_PREFIX = "station.views.counter."
COUNTER_OF_SUGGESTIONS_PREFIX = "station.suggestions.counter."

class StationApi():
	
	def __init__(self, shortname):
		self._shortname = shortname
		self._memcache_station_id = MEMCACHE_STATION_PREFIX + self._shortname
		self._memcache_station_queue_id = MEMCACHE_STATION_QUEUE_PREFIX + self._shortname
		self._memcache_station_sessions_id = MEMCACHE_STATION_SESSIONS_PREFIX + self._shortname
		self._memcache_station_broadcasts_id = MEMCACHE_STATION_BROADCASTS_PREFIX + self._shortname
		self._memcache_station_tracks_id = MEMCACHE_STATION_TRACKS_PREFIX + self._shortname
		self._memcache_station_buffer_id = MEMCACHE_STATION_BUFFER_PREFIX + self._shortname
		self._counter_of_broadcasts_id = COUNTER_OF_BROADCASTS_PREFIX + self._shortname
		self._counter_of_views_id = COUNTER_OF_VIEWS_PREFIX + self._shortname
		self._counter_of_suggestions_id = COUNTER_OF_SUGGESTIONS_PREFIX + self._shortname
	
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
	
	def put_station(self, page_id, shortname, page_name, page_link):
		station = Station(
			key_name = page_id,
			shortname = shortname,
			name = page_name,
			link = page_link,
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
	
	# Check if station is on air
	def on_air(self):
		on_air = False
		if(len(self.queue) > 0):
			on_air = True
				
		return on_air
	
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
				q.filter("station", self.station.key())
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
		
		# Init user
		user = None
		user_key = Session.user.get_value_for_datastore(session)
		if(user_key):
			# Load user proxy
			user_key_name = user_key.name()
			user_proxy = UserApi(user_key_name)
			user = user_proxy.user

		extended_session = Session.get_extended_session(session, user)
		
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
		
		# Init user
		user = None
		user_key = Session.user.get_value_for_datastore(session)
		if(user_key):
			# Load user proxy
			user_key_name = user_key.name()
			user_proxy = UserApi(user_key_name)
			user = user_proxy.user
		
		extended_session = Session.get_extended_session(session, user)
				
		new_sessions = []
		for s in self.sessions:
			if s["key_name"] != channel_id:
				new_sessions.append(s)
		
		memcache.set(self._memcache_station_sessions_id, new_sessions)
		logging.info("Session removed from memcache")
		
		return extended_session
	# Returns the current buffer of the station
	@property
	def buffer_and_timestamp(self):
		if not hasattr(self, "_buffer_and_timestamp"):
			self._buffer_and_timestamp = memcache.get(self._memcache_station_buffer_id)
			if self._buffer_and_timestamp is None:
				station = self.station
				buffer = self.station.buffer
				timestamp = self.station.timestamp

				self._buffer_and_timestamp = {'buffer':buffer, 'timestamp':timestamp}
				
				memcache.add(self._memcache_station_buffer_id, self._buffer_and_timestamp)
				logging.info("Buffer and timestamp put in memcache")
			else:
				logging.info("Buffer and timestamp retrieved from memcache")
		
		return self._buffer_and_timestamp

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
	
	# Returns the room in the queue
	def room(self):
		return(10 - len(self.queue))
	
	# Returns the station expiration time or the current time if there is no track in the tracklist
	def expiration_time(self):
		if not self.queue:
			logging.info("Queue empty")
			return datetime.utcnow()
		else:
			logging.info("Queue not empty")
			last_broadcast = self.queue[-1]
			return datetime.utcfromtimestamp(last_broadcast["expired"])
	
	def task_view(self):
		task = Task(
			url = "/taskqueue/view",
			params = {
				"shortname": self._shortname,
			}
		)
		task.add(queue_name = "worker-queue")
	
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
			
			for i in range(len(self.queue[1:])): 
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
	
	@property
	def number_of_broadcasts(self):
		if not hasattr(self, "_number_of_broadcasts"):
			shard_name = self._counter_of_broadcasts_id
			self._number_of_broadcasts = Shard.get_count(shard_name)
		return self._number_of_broadcasts
	
	# Starts a task that will increment the number of broadcasts
	def increment_broadcasts_counter(self):
		shard_name = self._counter_of_broadcasts_id
		Shard.task(shard_name, "increment")
	
	# Starts a task that will decrement the number of broadcasts
	def decrement_broadcasts_counter(self):
		shard_name = self._counter_of_broadcasts_id
		Shard.task(shard_name, "decrement")
	
	@property
	def number_of_views(self):
		if not hasattr(self, "_number_of_views"):
			shard_name = self._counter_of_views_id
			self._number_of_views = Shard.get_count(shard_name)
		return self._number_of_views
	
	def increase_views_counter(self, value):
		shard_name = self._counter_of_views_id
		Shard.increase(shard_name, value)
	
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
	
	def broadcasts_query(self, offset):
		q = Broadcast.all()
		q.filter("station", self.station.key())
		q.filter("created <", offset)
		q.order("-created")
		broadcasts = q.fetch(10)
		
		return broadcasts
		
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
		
		