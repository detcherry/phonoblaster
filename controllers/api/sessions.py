import logging

from datetime import datetime
from datetime import timedelta

from random import randrange
from calendar import timegm
from time import gmtime

import django_setup
from django.utils import simplejson as json

from google.appengine.api import channel

from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.session import Session
from models.db.story import SessionStory
from models.api.station import StationApi

class ApiSessionsHandler(BaseHandler):
	def get(self):		
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station
		number_of_sessions = station_proxy.number_of_sessions
		
		extended_sessions = None
		if(self.user_proxy):
			user = self.user_proxy.user
		
			q = SessionStory.all(keys_only = True)
			q.filter("receivers =", user.key())
			q.filter("station", station.key())
			q.filter("ended", None)
			q.filter("created >",  datetime.now() - timedelta(0,7200))
			session_story_keys = q.fetch(50) # Arbitrary number
		
			session_keys = [k.parent() for k in session_story_keys]
			sessions = Session.get(session_keys)
		
			extended_sessions = Session.get_extended_sessions(sessions)
		
		sessions_data = {
			"number": number_of_sessions,
			"friends": extended_sessions,
		}
			
		self.response.out.write(json.dumps(sessions_data))
		

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
			
			user_key = None
			if(self.user_proxy):
				user_key = self.user_proxy.user.key()
			
			# Put new session in datastore
			new_session = Session(
				key_name = new_channel_id,
				channel_token = new_channel_token,
				user = user_key,
			)
			new_session.put()
			logging.info("New session saved in datastore")

			output = {
				"channel_id": new_channel_id,
				"channel_token": new_channel_token,
			}

		self.response.out.write(json.dumps(output))
			