import logging
import os
from datetime import datetime
from calendar import timegm

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
		if not hasattr(self, "_stations"):
			self._station_ids =  memcache.get(self.memcache_onair)
			
			if self._station_ids is None:
				logging.info("Stations on air not in memcache")
				
				# We only fetch 400 tracks non expired 
				# If a station has a track non expired but he's not on this fetch, it will be placed later on in the memcache
				# (for instance when a new song is added to the memcache)
				q = Track.all()
				q.filter("expired >", datetime.now())
				q.order("-expired")
				not_expired_tracks = q.fetch(400)
				
				self._station_ids = set()
				for track in not_expired_tracks:
					station_key = Track.station.get_value_for_datastore(track)
					station_id = station_key.id()
					self._station_ids.add(station_id)
				
				# Put it in memcache
				memcache.set(self.memcache_onair, self._station_ids)
				logging.info("Stations on air put in memcache")
				
		return self._station_ids
	
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
		
		# Get stations on air
		stations_onair = self.stations
		
		# Collect memcache tracklist ids
		memcache_tracklist_ids = []
		for station_id in self.station_ids:
			memcache_tracklist_id = config.MEMCACHE_STATION_TRACKLIST_PREFIX + str(station_id)
			memcache_tracklist_ids.append(memcache_tracklist_id)
		
		# Collect all tracklists
		dict_tracklists = memcache.get_multi(memcache_tracklist_ids)
		index = 0
		for key, tracklist in dict_tracklists.iteritems():
			if(tracklist):
				for track in tracklist:
					# Only select the current track: the first track in the tracklist whose expiration time > now
					if(track.expired > datetime.now()):
						#tracks_onair.append(track)
						tracks_onair.append({
							"title":track.youtube_title,
							"thumbnail": track.youtube_thumbnail_url,
							"added": timegm(track.added.utctimetuple()),
						})
			else:
				# If tracklist not found in memcache, remove station from the air list
				tracks_onair.pop(index)
			
			# Incrememnt index
			index += 1
			
		# Zip stations and tracks
		stations_and_tracks = zip(stations_onair, tracks_onair)	
		
		return stations_and_tracks			
		
		
		
				
				
				
				
			
		