import logging
from datetime import datetime
from datetime import timedelta

from google.appengine.ext import db

from base import BaseHandler
from controllers import facebook
from models.db.station import Station
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

				q = Air.all()
				q.order("-created")
				feed = q.fetch(50)

				youtube_ids = [Air.youtube_id.get_value_for_datastore(f) for f in feed]
				extended_tracks = []
				for air in feed:
					extended_tracks.append({
						"id": air.youtube_id,
						"title": air.youtube_title,
						"duration": air.youtube_duration,
					})

				on_air = []
				stations = []
				tracks = []
				for f, e in zip(feed, extended_tracks):
					# Check if Youtube track exists
					if e:
						stations.append(f)
						tracks.append(e)
						if(f.expired > datetime.utcnow()):
							on_air.append(True)
						else:
							on_air.append(False)
			
				# Display all the user stations
				template_values = {
					"user_stations": user_stations,
					"feed": zip(stations, tracks, on_air),
				}
				self.render("home.html", template_values)
			
		else:
			self.render("welcome.html", None)