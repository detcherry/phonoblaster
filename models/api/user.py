import logging
import os
import re

from datetime import datetime
from datetime import timedelta
from calendar import timegm

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.taskqueue import Task

from controllers import facebook
from controllers import config

from models.db.user import User
from models.db.track import Track
from models.db.counter import Shard
from models.db.station import Station

from controllers.facebook import GraphAPIError

from models.api.admin import AdminApi

MEMCACHE_USER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".user."
MEMCACHE_USER_ACCOUNTS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".accounts.user."
MEMCACHE_USER_PROFILES_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".profiles.user."
MEMCACHE_USER_PROFILE_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".profile.user."

class UserApi:
	def __init__(self, uid, code):
		self._uid = uid
		self._code = code
		self._memcache_user_id = MEMCACHE_USER_PREFIX + self._uid
		self._memcache_user_accounts_id = MEMCACHE_USER_ACCOUNTS_PREFIX + self._uid
		self._memcache_user_profiles_id = MEMCACHE_USER_PROFILES_PREFIX + self._uid
		self._memcache_user_profile_id = MEMCACHE_USER_PROFILE_PREFIX + self._uid
	
	# Return the user 
	@property
	def user(self):
		if not hasattr(self, "_user"):
			self._user = memcache.get(self._memcache_user_id)
			if self._user is None:
				logging.info("User not in memcache")
				self._user = User.get_by_key_name(self._uid)
				if self._user:
					memcache.set(self._memcache_user_id, self._user)
					logging.info("%s %s put in memcache"%(self._user.first_name, self._user.last_name))
				else:
					logging.info("User does not exist")
			else:
				logging.info("%s %s already in memcache"%(self._user.first_name, self._user.last_name))
		return self._user	
	
	# Returns the user access token (facebook)
	@property
	def access_token(self):
		if not hasattr(self, "_access_token"):
			self._access_token = None
			if self._code:
				token_response = facebook.get_access_token_from_code(self._code, config.FACEBOOK_APP_ID, config.FACEBOOK_APP_SECRET)
				logging.info("Call to Facebook to retrieve access token")
				
				if "access_token" in token_response:
					self._access_token = token_response["access_token"][-1]
		
		return self._access_token
	
	# Puts new user in the datastore	
	def put_user(self, uid, first_name, last_name, email):
		user = User(
			key_name = uid,
			first_name = first_name,
			last_name = last_name,
			email = email,
			stations = self.stations,
		)
		user.put()
		logging.info("User put in datastore")

		# Put the user in the proxy
		self._user = user
		
		# Increment admin counter of users
		admin_proxy = AdminApi()
		admin_proxy.increment_users_counter()
		logging.info("Counter of users incremented")
		
		# Mail new user to admins
		self.mail()
		
		return self._user	
	
	def mail(self):
		admin_proxy = AdminApi()
		
		subject = "New phonoblaster user: %s %s" % (self.user.first_name, self.user.last_name)
		body = """
A new user has logged into Phonoblaster:
%s %s, %s
		
Global number of users: %s
		""" %(self.user.first_name, self.user.last_name, self.user.email, admin_proxy.number_of_users)
		
		task = Task(
			url = "/taskqueue/mail",
			params = {
				"to": "activity@phonoblaster.com",
				"subject": subject,
				"body": body,
			}
		)
		task.add(queue_name = "worker-queue")

	# Return the user accounts (pages he's admin of on Facebook)
	@property
	def accounts(self):
		if not hasattr(self, "_accounts"):
			self._accounts = None
			graph = facebook.GraphAPI(self.access_token)
			try:
				results = graph.get_connections(str(self._uid),"accounts")["data"]
				logging.info("Call to Facebook to retrieve user accounts")
			except GraphAPIError:
				results = []
				logging.info("Graph API Error")
			
			accounts = []
			for r in results:
				if(r["category"] != "Application"):
					accounts.append({
						"page_name" : r["name"],
						"page_id"	: r["id"],
					})
					
			self._accounts = accounts
			
		return self._accounts
	
	@property
	def stations(self):
		stations = []
		user = [db.Key.from_path('Station', str(self._uid))]
		accounts = [db.Key.from_path('Station', a["page_id"]) for a in self.accounts]
		
		stations = user + accounts
		
		return stations
	
	def update_stations(self):
		if(self.access_token):
			self.user.stations = self.stations
			self.user.put()
			logging.info("User stations updated in datastore")
		
			memcache.set(self._memcache_user_id, self.user)
			logging.info("User updated in memcache")
		else:
			logging.info("User stations not updated: no access token")

	# Tells if a user is an admin of a specific station
	def is_admin_of(self, key_name):
		for key in self.user.stations:
			if(str(key.name()) ==  key_name):
				return True
		return False

################################################################################################################################################
#											PROFILE ITERATION
################################################################################################################################################
	@property
	def profile(self):
		if not hasattr(self, "_profile"):
			self._profile = memcache.get(self._memcache_user_profile_id)
			if self._profile is None:
				logging.info("User Profile not in memcache")
				user = self.user
				if user is not None:
					profile_ref = self.user.profile
					if profile_ref is not None:
						station = db.get(profile_ref.key())
						if station:
							self._profile = {
								"key_name": station.key().name(),
								"shortname": station.shortname,
								"name": station.name,
								"type": station.type,
								"link": station.link
							}
							memcache.set(self._memcache_user_profile_id, self._profile)
							logging.info("%s %s's profile put in memcache"%(user.first_name, user.last_name))
						else:
							logging.error("Profile refers to a non existing station!")
					else:
						logging.info("User has no profile yet.")
				else:
					logging.info("User does not exist")
			else:
				logging.info("%s %s's profile already in memcache"%(self.user.first_name, self.user.last_name))
		return self._profile	
	
	@property
	def profiles(self):
		if not hasattr(self, "_profiles"):
			self._profiles = memcache.get(self._memcache_user_profiles_id)
			
			if(self._profiles is None):
				self._profiles = []
				
				if(self.user.updated < datetime.utcnow() - timedelta(1,0)):
					logging.info('Last update > 24h ago, need to update user stations')
					self.update_stations()
				else:
					logging.info('Last update < 24h ago, no need to update user stations')
									
				stations_keys = self.user.stations
				stations = db.get(stations_keys)
				logging.info("Stations retrieved from datastore")
				
				graph = facebook.GraphAPI()
				ids = [k.name() for k in stations_keys]
				objects = graph.get_objects(ids)
				logging.info("Objects retrieved from Facebook")
				
				for i in xrange(0, len(stations_keys)):
					key = stations_keys[i]
					station = stations[i]
					
					p = {}
					if(station):
						# Associated profile already created
						p = {
							"key_name": station.key().name(),
							"shortname": station.shortname,
							"name": station.name,
							"type": station.type,
							"link": station.link,
							"created": station.created
						}
					else:
						# Associated profile not already created
						p = {
							"shortname": None,
							"link": None,
							"created": None,
						}
						
						if(i==0):
							# User profile
							p.update({
								"key_name": self.user.key().name(),
								"name": self.user.first_name + " " + self.user.last_name,
								"type": "user",
							})
						else:
							if(key.name() in objects):
								# Published page profile
								p.update({
									"key_name": objects[key.name()]["id"],
									"name": objects[key.name()]["name"],
									"type": "page",
								})
							else:
								# Unpublished page profile
								p = {}
					
					if(p):
						self._profiles.append(p)

				memcache.set(self._memcache_user_profiles_id, self._profiles)
				logging.info("%s %s's profiles put in memcache" % (self.user.first_name, self.user.last_name))
			else:
				logging.info("%s %s's profiles already in memcache" % (self.user.first_name, self.user.last_name))
		
		return self._profiles
	
	def set_profile(self, key_name):
		# We first need to check if key_name is in the profiles of the user
		profile = None
		for i in xrange(0,len(self.profiles)):
			if key_name == self.profiles[i]["key_name"]:
				profile = self.profiles[i]
				break

		if profile:
			# Retrieving the associated station
			station_key = db.Key.from_path("Station", profile["key_name"])
			station = db.get(station_key)
			
			user = self.user
			user.profile = station_key
			user.put()
			logging.info("User put in datastore")
			
			memcache.set(self._memcache_user_id, self._user)
			logging.info("User put in memcache")
			
			# User put in runtime
			self._user = user

			# Setting profile in memecache and runtime
			self._profile = {
				"key_name": station.key().name(),
				"shortname": station.shortname,
				"name": station.name,
				"type": station.type,
				"link": station.link
			}
			memcache.set(self._memcache_user_profile_id, self._profile)
			logging.info("User profile set in memcache.")

		else:
			logging.info("Rejected, key_name not in user profiles")


