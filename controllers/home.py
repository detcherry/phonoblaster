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
			user_profile = StationApi(self.user_proxy.profile["shortname"])
			user_broadcasts = user_profile.reorder_buffer(user_profile.buffer)["broadcasts"]
			user_live_broadcast = None
			if(len(user_broadcasts)>0):
				user_live_broadcast = user_broadcasts[0]

			live_broadcasts = []
			latest_active_stations = []
			
			q = Station.all()
			q.order("-active")
			stations = q.fetch(30)
			logging.info(str(len(stations))+" latest stations retrieved from datastore")

			all_broadcasts_keys = []
			for i in xrange(0,len(stations)):
				all_broadcasts_keys.extend(stations[i].broadcasts)
			
			all_broadcasts = db.get(all_broadcasts_keys)
			logging.info(str(len(all_broadcasts))+" broadcasts associated with stations retrieved from datastore")			
			
			couple = {}
			for s in stations:
				name = str(s.key().name())
				couple[name] = {
					"station": s,
					"broadcasts": [],
					"live": None,
				}
				
			for b in all_broadcasts:
				name = str(Broadcast.station.get_value_for_datastore(b).name())
				couple[name]["broadcasts"].append(b)
			logging.info("Broadcasts group by station")
						
			# What is the live track for each station?
			now = datetime.utcnow()
			for k, v in couple.iteritems():
				station = v["station"]
				broadcasts = v["broadcasts"]
				
				timestamp = station.timestamp
				
				elapsed = 0
				live = None
				
				total_duration = 0
				for broadcast in broadcasts:
					if(broadcast.youtube_duration):
						total_duration += broadcast.youtube_duration
					else:
						if(broadcast.soundcloud_duration):
							total_duration += broadcast.soundcloud_duration
						else:
							total_duration += 0
				
				# Check if buffer is not empty
				if total_duration > 0:
					offset = (timegm(now.utctimetuple()) - timegm(timestamp.utctimetuple())) % total_duration
					for broadcast in broadcasts:
						if(broadcast.youtube_id):
							id = broadcast.youtube_id
							title = broadcast.youtube_title
							duration = broadcast.youtube_duration
							thumbnail = "https://i.ytimg.com/vi/" + broadcast.youtube_id + "/default.jpg"
						else:
							id = broadcast.soundcloud_id
							title = broadcast.soundcloud_title
							duration = broadcast.soundcloud_duration
							thumbnail = broadcast.soundcloud_thumbnail
													
						# Current broadcast math pattern below
						if elapsed + duration > offset:
							live = {
								'id': id,
								'title': title,
								'duration': duration,
								'thumbnail': thumbnail,
							}
							
							couple[k]["live"] = live							
							break

						# We must keep browsing the list before finding the current track
						else:
							elapsed += duration
			logging.info("Live broadcast determined for each station")
			
			for s in stations:
				name = s.key().name()
				if(couple[name]["live"]):
					latest_active_stations.append(couple[name]["station"])
					live_broadcasts.append(couple[name]["live"])
			
			# Display all the user stations
			template_values = {
				"number_of_sessions": user_profile.number_of_sessions,
				"live": user_live_broadcast,
				"feed": zip(latest_active_stations, live_broadcasts),
			}
			self.render("home.html", template_values)
			
		else:
			self.render("welcome.html", None)