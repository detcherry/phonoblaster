import logging
import os

from google.appengine.ext import db
from google.appengine.api import memcache

from models.db.station import Station

MEMCACHE_STATION_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".station."
MEMCACHE_STATION_QUEUE_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".queue.station."
MEMCACHE_STATION_SESSIONS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".sessions.station."

class StationApi():
	
	def __init__(self, shortname):
		self._shortname = shortname
		self._memcache_station_id = MEMCACHE_STATION_PREFIX + self._shortname
		self._memcache_station_queue_id = MEMCACHE_STATION_QUEUE_PREFIX + self._shortname
		self._memcache_station_sessions_id = MEMCACHE_STATION_SESSIONS_PREFIX + self._shortname
	
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
	
