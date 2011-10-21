import logging

from models.interface import config

from google.appengine.ext import db
from google.appengine.api import memcache
from models.db.user import User

class InterfaceUser():
	
	def __init__(self, user_key = None, facebook_id = None):
		
		if user_key:
			logging.info("User proxy initialized with key")
			self._user_key = db.Key(str(user_key))
			
		elif facebook_id:
			logging.info("User proxy initialized with facebook id")
			self.memcache_user_facebook_id = config.MEMCACHE_USER_FACEBOOK_PREFIX + str(facebook_id)
			self._user = memcache.get(self.memcache_user_facebook_id)
			
			if self._user is None:
				logging.info("User not in memcache")
				self._user = User.all().filter("facebook_id", facebook_id).get()
				
				if self._user:
					logging.info("User exists")
					self._user_key = self._user.key()
					self.memcache_user_id = config.MEMCACHE_USER_PREFIX	+ str(self._user_key.id())
					memcache.set_multi({
						self.memcache_user_id: self._user,
						self.memcache_user_facebook_id: self._user,
					})
					logging.info("User loaded TWICE in memcache (key and facebook id)")
				else:
					self._user_key = None
					logging.info("User does not exist")
			else:
				self._user_key = self._user.key()
				logging.info("User already in memcache")
		
		else:
			logging.info("User proxy initialized without key or facebook id")
		
		if(self._user_key):
			self.memcache_user_id = config.MEMCACHE_USER_PREFIX	+ str(self._user_key.id())
	
	
	# Get the user
	@property
	def user(self):
		if not hasattr(self, "_user"):
			self._user = memcache.get(self.memcache_user_id)
			if self._user is None:
				logging.info("User not in memcache")
				self._user = User.get(self._user_key)
				if self._user:
					logging.info("User exists")
					self.memcache_user_facebook_id = config.MEMCACHE_USER_FACEBOOK_PREFIX + str(self._user.facebook_id)
					memcache.set_multi({
						self.memcache_user_id: self._user,
						self.memcache_user_facebook_id: self._user,
					})
					logging.info("User loaded TWICE in memcache (key and facebook id)")
				else:
					logging.info("User does not exist")
			else:
				logging.info("User already in memcache")
		
		return self._user	
	
	# Put the user for the first time
	def put_user(self, facebook_id = None, facebook_access_token = None, name = None, first_name = None, last_name = None, email = None):
		if facebook_id and name and first_name and last_name:			
			user = User(
				facebook_id = facebook_id,
				facebook_access_token = facebook_access_token,
				name = name,
				first_name = first_name,
				last_name = last_name,
				public_name = first_name + " " + last_name[0] + ".",
				email = email
			)
			user.put()
			logging.info("User put in datastore")
			
			self._user = user
			self._user_key = self._user.key()
			self.memcache_user_id = config.MEMCACHE_USER_PREFIX + str(self._user_key.id())	
			self.memcache_user_facebook_id = config.MEMCACHE_USER_FACEBOOK_PREFIX + str(self._user.facebook_id)
			
			memcache.set_multi({
				self.memcache_user_id: self._user,
				self.memcache_user_facebook_id: self._user,
			})
			logging.info("User put in memcache")
			
			return user
		else:
			raise ValueError("A user must have at least facebook_id, name, first name and last name")
		
		
	# Update the user information
	def update_user(self, facebook_access_token = None, name = None, first_name = None, last_name = None, email = None):
		if facebook_access_token:
			self.user.facebook_access_token = facebook_access_token
			logging.info("New access token")
		if name and first_name and last_name:
			self.user.name = name
			self.user.first_name = first_name
			self.user.last_name = last_name
			self.user.public_name = first_name + " " + last_name[0] + "."
		if email:
			self.user.email = email
			logging.info("New email")
			
		self.user.put()
		logging.info("New user information put in datastore")
		
		memcache.set_multi({
			self.memcache_user_id: self.user,
			self.memcache_user_facebook_id: self.user,
		})
		logging.info("New user information put in memcache")
		
		return self.user

		
		
		
		
			