import logging
from datetime import datetime
from datetime import timedelta
from calendar import timegm

from google.appengine.ext import db

from base import profile_required
from base import BaseHandler
from controllers import facebook
from models.db.station import Station
from models.api.station import StationApi
from models.db.broadcast import Broadcast

class HomeHandler(BaseHandler):
	@profile_required
	def get(self):
		if(self.user_proxy):
			user = self.user_proxy.user
			user_profile = self.user_proxy.profile

			"""
			live_broadcasts = []
			latest_active_stations = []
			
			q = Station.all()
			q.order("-updated")
			stations = q.fetch(30)
			logging.info(str(len(stations))+" latest stations retrieved from datastore")

			all_broadcasts_keys = []
			for i in xrange(0,len(stations)):
				all_broadcasts_keys.extend(stations[i].broadcasts)
			
			all_broadcasts = db.get(all_broadcasts_keys)
			logging.info(str(len(all_broadcasts))+" broadcasts associated with stations retrieved from datastore")			
			
			broadcasts_group_by_station = []
			for i in xrange(0, len(stations)):
				host = stations[i]
				host_key = host.key()
				
				broadcasts = []
				for j in xrange(0, len(all_broadcasts)):
					broadcast = all_broadcasts[j]
					broadcast_host_key = Broadcast.station.get_value_for_datastore(broadcast)
					
					if(host_key == broadcast_host_key):
						broadcasts.append(broadcast)
				
				broadcasts_group_by_station.append(broadcasts)
			logging.info("Broadcasts group by station")
			
			# What is the live track for each station?
			now = datetime.utcnow()			
			for station, broadcasts in zip(stations, broadcasts_group_by_station):
				timestamp = station.timestamp
				
				elapsed = 0
				live = None
				
				total_duration = 0
				for i in xrange(0, len(broadcasts)):
					total_duration += broadcasts[i].youtube_duration
				
				# Check if buffer is not empty
				if total_duration > 0:
					offset = (timegm(now.utctimetuple()) - timegm(timestamp.utctimetuple())) % total_duration
					for broadcast in broadcasts:
						duration = broadcast.youtube_duration			
						
						# Current broadcast math pattern below
						if elapsed + duration > offset:
							live = {
								'id': broadcast.youtube_id,
								'title': broadcast.youtube_title,
								'duration': broadcast.youtube_duration
							}
							
							latest_active_stations.append(station)
							live_broadcasts.append(live)
							
							break

						# We must keep browsing the list before finding the current track
						else:
							elapsed += duration
			"""
			
			live_broadcasts = []
			latest_active_stations = []
			sorted_broadcasts_by_station = [] # needed after accessing data from datastore
			sorted_tracks_by_station = []
			sorted_stations = []

			q = Station.all()
			q.order("-updated")
			feed = q.fetch(30)
			logging.info(str(len(feed))+" latest stations retrieved from datastore")

			broadcasts_keys = []
			for i in xrange(0,len(feed)):
				broadcasts_keys.extend(feed[i].broadcasts)
				sorted_broadcasts_by_station.append([])
				sorted_tracks_by_station.append([])

			broadcasts = db.get(broadcasts_keys)
			logging.info(str(len(broadcasts))+" Broadcasts associated with stations retrieved from datastore")

			# Retrieving tracks associated with tracks
			tracks_keys = []
			for i in xrange(0,len(broadcasts)):
				tracks_keys.append(Broadcast.track.get_value_for_datastore(broadcasts[i]))

			tracks = db.get(tracks_keys)
			logging.info(str(len(tracks))+" Tracks associated with broadcasts retrieved from datastore")

			# Sorting broadcasts
			while len(broadcasts) >0:
				b = broadcasts.pop(0)
				t = tracks.pop(0)
				station_key = Broadcast.station.get_value_for_datastore(b)

				for i in xrange(0,len(sorted_broadcasts_by_station)):

					if len(sorted_broadcasts_by_station[i]) == 0 :
						# Empty list, we fil it with the current broadcast
						sorted_broadcasts_by_station[i].append(b)
						sorted_tracks_by_station[i].append(t)

						# Looking for corresponding station entity
						for j in xrange(0,len(feed)):
							key = feed[j].key()
							if key == station_key:
								sorted_stations.append(feed[j])
								break
						break
					
					if  station_key == Broadcast.station.get_value_for_datastore(sorted_broadcasts_by_station[i][0]):
						# We found a not empty list corresponding to the right station
						sorted_broadcasts_by_station[i].append(b)
						sorted_tracks_by_station[i].append(t)
						break
			logging.info(str(len(sorted_broadcasts_by_station))+" Broadcasts sorted by station")

			# What is the live track for each station?
			now = datetime.utcnow()
			for i in xrange(0, len(sorted_stations)):
				station = sorted_stations[i]
				if station.type == "user":
					station.is_page = False
				else:
					station.is_page = True
				tracks = sorted_tracks_by_station[i]
				timestamp = station.timestamp

				elapsed = 0
				new_live_item = None
				start = 0

				buffer_duration = 0
				for j in xrange(0,len(tracks)):
					buffer_duration += tracks[j].youtube_duration

				if buffer_duration > 0:
					offset = (timegm(now.utctimetuple()) - timegm(timestamp.utctimetuple())) % buffer_duration

					for j in xrange(0,len(tracks)):
						item = tracks[j]
						duration = item.youtube_duration

						# This is the current broadcast
						if elapsed + duration > offset :
							live_item = {
								'id': item.youtube_id,
								'title': item.youtube_title,
								'duration': item.youtube_duration
							}
							latest_active_stations.append(station)
							live_broadcasts.append(live_item)
							break

						# We must keep browsing the list before finding the current track
						else:
							elapsed += duration
				else:
					logging.info("Buffer is empty")
			logging.info(str(len(live_broadcasts))+" Live items found for "+str(len(latest_active_stations))+" stations")
			
			# Display all the user stations
			template_values = {
				"user_profile": user_profile,
				"feed": zip(latest_active_stations, live_broadcasts),
			}
			self.render("home.html", template_values)
			
		else:
			self.render("welcome.html", None)