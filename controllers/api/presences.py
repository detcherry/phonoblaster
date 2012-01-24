import logging
from random import randrange
from calendar import timegm
from time import gmtime
import django_setup
from django.utils import simplejson as json

from google.appengine.api import channel

from controllers.base import BaseHandler
from models.db.presence import Presence
from models.api.station import StationApi

class ApiPresencesHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		presences = station_proxy.presences
		self.response.out.write(json.dumps(presences))
	
	def post(self):
		shortname = self.request.get("shortname")
		self.station_proxy = StationApi(shortname)
		self.station = self.station_proxy.station 
		
		output = {}
		if(self.station):
			# Channel ID and token generation
			time_now = str(timegm(gmtime()))
			random_integer = str(randrange(1000))
			new_channel_id = shortname + "." + time_now + random_integer
			new_channel_token = channel.create_channel(new_channel_id)

			# Check if user logged in
			user_key = None	
			admin = False
			if(self.user_proxy):
				user_key = self.user_proxy.user.key()
				if(self.user_proxy.is_admin_of(self.station.key().name())): 
					admin = True
		
			# Put new presence in datastore
			new_presence = Presence(
				key_name = new_channel_id,
				channel_token = new_channel_token,
				station = self.station.key(),
				user = user_key,
				admin = admin,
			)
			new_presence.put()
			logging.info("New station presence saved in datastore")
		
			output = {
				"channel_id": new_channel_id,
				"channel_token": new_channel_token,
			}
		self.response.out.write(json.dumps(output))