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
			
			# Display all the user stations
			template_values = {
				"user_profile": user_profile,
				"feed": zip(latest_active_stations, live_broadcasts),
			}
			self.render("home.html", template_values)
			
		else:
			self.render("welcome.html", None)