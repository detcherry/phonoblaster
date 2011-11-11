import logging
import os
from datetime import datetime

from models.interface import config
from models.db.track import Track
from models.db.station import Station

from google.appengine.ext import db
from google.appengine.api import memcache

class InterfaceOnAir():
	
	def __init__(self):
		self.memcache_onair = config.MEMCACHE_ONAIR 
	
	# Returns all stations on the air
	@property
	def station_ids(self):
		if not hasattr(self, "_station_ids"):
			self._station_ids =  memcache.get(self.memcache_onair)
			
			if self._station_ids is None:
				logging.info("Stations on air not in memcache")
				self._station_ids = set()
			else:
				logging.info("Stations on the air already in memcache")
				
		return self._station_ids
	
	# Add stations in the on the air list
	def add_station_id(self, id):
		new_station_ids = self.station_ids
		# As we're using a set, there won't be any duplicate
		new_station_ids.add(str(id))
		
		# Put it in memecache
		memcache.set(self.memcache_onair, new_station_ids)
		logging.info("New station on the air put in memcache")
			
	# Remove stations in the on the air list
	def remove_station_id(self, id):
		new_station_ids = self.station_ids
		try:
			new_station_ids.remove(str(id))
			memcache.set(self.memcache_onair, new_station_ids)
			logging.info("Station not anymore on the air removed from memcache")
		except KeyError:
			logging.info("Station not anymore on the air not in memcache")

	# Returns the stations that are on the air
	@property
	def stations(self):
		stations_onair = []
		
		# Generate the memcache IDs from the station IDs
		memcache_station_ids = []
		for station_id in self.station_ids:
			memcache_station_id = config.MEMCACHE_STATION_PREFIX + str(station_id)
			memcache_station_ids.append(memcache_station_id)
		
		# Get the stations from the memcache in bulk
		dict_stations_onair = memcache.get_multi(memcache_station_ids)
		
		# Remove any station that has not been found in memcache
		for key, station in dict_stations_onair.iteritems():
			if(station):
				stations_onair.append(station)
		
		return stations_onair
				
	# Returns the stations that are on the air + the current track on air in this station
	@property
	def stations_and_tracks(self):
		stations_onair = []
		tracks_onair = []
		onair = dict()
		
		# ------------ stations ------------------
		
		# Generate the memcache IDs from the station IDs
		memcache_station_ids = []
		for station_id in self.station_ids:
			memcache_station_id = config.MEMCACHE_STATION_PREFIX + str(station_id)
			memcache_station_ids.append(memcache_station_id)
		logging.info("Memcache ids for stations on the air built")
		
		# Get the stations from the memcache in bulk
		dict_stations_onair = memcache.get_multi(memcache_station_ids)
		
		# Remove any station that has not been found in memcache
		for key, station in dict_stations_onair.iteritems():
			if(station):
				id_of_station = key.replace(config.MEMCACHE_STATION_PREFIX, "")
				onair[id_of_station] = { "station": station }
		
		
		logging.info("Stations on the air retrieved")
		
		# ------------- tracklist -----------------
		
		# Collect memcache tracklist ids
		memcache_tracklist_ids = []
		for station_id in self.station_ids:
			memcache_tracklist_id = config.MEMCACHE_STATION_TRACKLIST_PREFIX + str(station_id)
			memcache_tracklist_ids.append(memcache_tracklist_id)
		logging.info("Memcache ids for tracklists on the air built")
		
		# Collect all tracklists
		dict_tracklists = memcache.get_multi(memcache_tracklist_ids)
		index = 0
		for key, tracklist in dict_tracklists.iteritems():
			id_of_station = key.replace(config.MEMCACHE_STATION_TRACKLIST_PREFIX, "")
			
			if(tracklist and len(tracklist)>0):
				current_track = None;
				for track in tracklist:
					# Only select the current track: the first track in the tracklist whose expiration time > now
					if(track.expired > datetime.now()):
						current_track = track
						break
				
				if(current_track):
					onair[id_of_station]["track"] = current_track
					
				else:
					# There is no current track in the list so we can remove station from the on the air list
					del onair[id_of_station]
					self.remove_station_id(id_of_station)
						
			else:
				# If tracklist not found in memcache or empty, remove station from the on the air list
				del onair[id_of_station]
				self.remove_station_id(id_of_station)
			
			# Incremement index
			index += 1
		logging.info("Tracks on the air retrieved")
		
		for key, dictio in onair.iteritems():
			stations_onair.append(dictio["station"])
			tracks_onair.append(dictio["track"])
		
		# Zip stations and tracks on air
		stations_and_tracks = zip(stations_onair, tracks_onair)	
		
		return stations_and_tracks			
		
		
		
				
				
				
				
			
		