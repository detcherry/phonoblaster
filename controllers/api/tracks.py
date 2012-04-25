import logging
from datetime import datetime

import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler
from controllers.base import login_required

from google.appengine.ext import db

from models.db.track import Track
from models.db.broadcast import Broadcast
from models.db.favorite import Favorite

from models.api.station import StationApi

from controllers.base import login_required

class ApiTracksHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		offset = self.request.get("offset")
		station_proxy = StationApi(shortname)
		
		if(station_proxy.station and offset):
			extended_tracks = station_proxy.get_tracks(datetime.utcfromtimestamp(int(offset)))
			self.response.out.write(json.dumps(extended_tracks))
		else:
			self.error(404)

class ApiTracksDeleteHandler(BaseHandler):
	@login_required
	def delete(self, id):
		logging.info("In ApiTracksDeleteHandler")
		logging.info(id)

		track = Track.get_by_id(int(id))

		if(track):
			#Deleting associated broadcasts
			query = Broadcast.all().filter("track", track)
			broadcasts = query.fetch(1000)

			while(len(broadcasts)>0):
				db.delete(broadcasts)
				broadcasts = query.fetch(1000)

			#Deleting associated favorites
			query = Favorite.all().filter("track", track)
			favorites = query.fetch(1000)

			while(len(favorites)>0):
				db.delete(favorites)
				favorites = query.fetch(1000)

			db.delete(track)

			response = True
		else:
			response = False




		self.response.out.write(json.dumps({ "response": response }))