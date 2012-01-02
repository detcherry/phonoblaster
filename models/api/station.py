import logging
import os

from datetime import datetime
from datetime import timedelta
from calendar import timegm

from google.appengine.ext import db
from google.appengine.api import memcache

from models.db.station import Station
from models.db.presence import Presence
from models.db.comment import Comment

MEMCACHE_STATION_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".station."
MEMCACHE_STATION_QUEUE_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".queue.station."
MEMCACHE_STATION_PRESENCES_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".presences.station."

class StationApi():
	
	def __init__(self, shortname):
		self._shortname = shortname
		self._memcache_station_id = MEMCACHE_STATION_PREFIX + self._shortname
		self._memcache_station_queue_id = MEMCACHE_STATION_QUEUE_PREFIX + self._shortname
		self._memcache_station_presences_id = MEMCACHE_STATION_PRESENCES_PREFIX + self._shortname
	
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
	
	# Check if station is on air
	@property
	def on_air(self):
		return False

	# Format an extended presence (what is stored in memcache)
	def format_extended_presences(self, presences):
		extended_presences = []
		
		admins_presences = []
		authenticated_presences = []
		unauthenticated_presences = []
		
		user_keys = []
		
		# Dispatch admin, authenticated and unauthenticated presences
		for p in presences:
			if(p.admin):
				admins_presences.append(p)
			else:
				user_key = Presence.user.get_value_for_datastore(p)
				if user_key:
					authenticated_presences.append(p)
					user_keys.append(user_key)
				else:
					unauthenticated_presences.append(p)
		
		# Add the extended presences for admins
		for presence in admins_presences:
			extended_presences.append({
				"channel_id": presence.key().name(),
				"created": timegm(presence.created.utctimetuple()),
				"listener_key_name": self.station.key().name(),
				"listener_name": self.station.name,
				"admin": True,
			})
		
		# Retrieve users of authenticated presences
		users = db.get(user_keys)
		
		# Add the extended presences for authenticated users
		for presence, user in zip(authenticated_presences, users):
			extended_presences.append({
				"channel_id": presence.key().name(),
				"created": timegm(presence.created.utctimetuple()),
				"listener_key_name": user.key().name(),
				"listener_name": user.first_name + " " + user.last_name,
				"admin": False,
			})
		
		# Add the extended presences for unauthenticated users
		for presence in unauthenticated_presences:
			extended_presences.append({
				"channel_id": presence.key().name(),
				"created": timegm(presence.created.utctimetuple()),
				"user_key_name": None,
				"user_name": None,
				"admin": False,
			})
			
		return extended_presences

	# Return the list of users connected to a station
	@property
	def presences(self):
		if not hasattr(self, "_presences"):
			self._presences = memcache.get(self._memcache_station_presences_id)
			if self._presences is None:
				self._presences = []
				logging.info("Presences not in memcache")
				q = Presence.all()
				q.filter("station", self.station.key())
				q.filter("connected", True)
				q.filter("ended", None)
				q.filter("created >",  datetime.now() - timedelta(0,7200))
				presences = q.fetch(1000) # Max number of entities App Engine can fetch in one call
				
				# Format extended presences
				self._presences = self.format_extended_presences(presences)
				
				# Put extended presences in memcache
				memcache.set(self._memcache_station_presences_id, self._presences)
				logging.info("Presences loaded in memcache")
			else:
				# We clean up the presences list in memcache
				cleaned_up_presences_list = []
				token_timeout = datetime.now() - timedelta(0,7200)
				limit = timegm(token_timeout.utctimetuple())
				
				for presence in self._presences:
					if(presence["created"] > limit):
						cleaned_up_presences_list.append(presence)
				
				if(len(cleaned_up_presences_list) != len(self._presences)):
					self._presences = cleaned_up_presences_list
					memcache.set(self._memcache_station_presences_id, self._presences)
					logging.info("Presences list already in memcache and cleaned up")
				else:
					logging.info("Presences list already in memcache but no need to clean up")
			
		return self._presences

	# Add a presence to a station
	def add_presence(self, channel_id):
		# Get presence from datastore 
		presence = Presence.get_by_key_name(channel_id)
		
		extended_presence = None
		if(presence):
			# Format presence into extended presence
			extended_presence = self.format_extended_presences([presence])[0]

			# Add it to the list in memcache
			self.presences.append(extended_presence)

			# Put new list in memcache
			memcache.set(self._memcache_station_presences_id, self._presences)
			logging.info("New presence put in memcache")
			
			# Put new present in datastore
			presence.connected = True
			presence.put()
			logging.info("Presence updated in datastore")

		return extended_presence
	
	# Remove a presence from a station
	def remove_presence(self, channel_id):
		# Get presence from datastore 
		presence = Presence.get_by_key_name(channel_id)
		
		presence_gone = None
		if(presence):	
			# Format presence gone into extended presence
			presence_gone = self.format_extended_presences([presence])[0]

			# Update presences list
			updated_presences = []
			for p in self.presences:
				if(p["channel_id"] != presence_gone["channel_id"]):
					updated_presences.append(p)

			# Put new list in proxy
			self._presences = updated_presences
			# Put new list in memcache
			memcache.set(self._memcache_station_presences_id, self._presences)
			logging.info("Presence removed from memcache")
			
			# Update presence in datastore
			presence.ended = datetime.now()
			presence.put()
			logging.info("Presence updated in datastore")

		return presence_gone
	
	# Returns the current station queue
	@property
	def queue(self):
		return "queue"
		
		
