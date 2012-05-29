import logging
from datetime import datetime
from datetime import timedelta

from google.appengine.ext import db

from base import BaseHandler
from controllers import facebook
from models.db.station import Station
from models.api.station import StationApi
from models.db.air import Air
from models.db.track import Youtube

class HomeHandler(BaseHandler):
	def get(self):
		if(self.user_proxy):
			user = self.user_proxy.user
			# User has been put less than 5 secs ago
			if(user.created > datetime.utcnow() - timedelta(0,5)):
				self.redirect("/station/create")
			else:
				user_stations = self.user_proxy.stations

				q = Station.all()
				q.order("-updated")
				feed = q.fetch(10)

				live_broadcasts = []
				latest_active_stations = []

				for station in feed:
					station_proxy = StationApi(station.shortname)
					buffer = station_proxy.reorder_buffer(station_proxy.buffer)
					
					if buffer:
						latest_active_stations.append(station)
						live_broadcast = buffer['broadcasts'][0]
						live_broadcasts.append({
							"id": live_broadcast['youtube_id'],
							"title": live_broadcast['youtube_title'],
							"duration": live_broadcast['youtube_duration'],
						})

			
				# Display all the user stations
				template_values = {
					"user_stations": user_stations,
					"feed": zip(latest_active_stations, live_broadcasts),
				}
				self.render("home.html", template_values)
			
		else:
			self.render("welcome.html", None)