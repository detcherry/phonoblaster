import logging

from google.appengine.ext import db
from google.appengine.api import memcache

from models.api import config
from models.db.user import User

class UserApi():
	
	def __init__(self, username):
		self._username = username
		self._memcache_user_id = config.MEMCACHE_USER_PREFIX + username
		self._memcache_user_tracks_id = config.MEMCACHE_TRACKS_USER_PREFIX + username
		self._memcache_user_sessions_id = config.MEMCACHE_SESSIONS_USER_PREFIX + username
			
	# Returns the user
	@property
	def user(self):
		if not hasattr(self, "_user"):
			self._user = memcache.get(self._memcache_user_id)
			if self._user is None:
				logging.info("User not in memcache")
				self._user = User.all().filter("username", self._username).get()
				if self._user:
					logging.info("User exists")
					memcache.set(self._memcache_user_id, self._user)
					logging.info("@%s put in memcache"%(self._user.username))
				else:
					logging.info("User does not exist")
			else:
				logging.info("@%s already in memcache"%(self._user.username))
		return self._user
					
					
					
					
					
					
		