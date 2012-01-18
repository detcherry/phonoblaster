import logging
import os

from datetime import datetime
from calendar import timegm

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api.taskqueue import Task

from controllers import facebook
from models.db.user import User
from models.db.favorite import Favorite
from models.db.counter import Shard

MEMCACHE_USER_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".user."
MEMCACHE_USER_CONTRIBUTIONS_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".contributions.user."
MEMCACHE_USER_FAVORITES_PREFIX = os.environ["CURRENT_VERSION_ID"] + ".favorites.user."
COUNTER_OF_FAVORITES = "user.favorites.counter."

class UserApi:
	def __init__(self, facebook_id):
		self._facebook_id = str(facebook_id)
		self._memcache_facebook_id = MEMCACHE_USER_PREFIX + self._facebook_id
		self._memcache_user_contributions_id = MEMCACHE_USER_CONTRIBUTIONS_PREFIX + self._facebook_id
		self._memcache_user_favorites_id = MEMCACHE_USER_FAVORITES_PREFIX + self._facebook_id
		self._counter_of_favorites_id = COUNTER_OF_FAVORITES + self._facebook_id
	
	# Return the user
	@property
	def user(self):
		if not hasattr(self, "_user"):
			self._user = memcache.get(self._memcache_facebook_id)
			if self._user is None:
				logging.info("User not in memcache")
				self._user = User.get_by_key_name(self._facebook_id)
				if self._user:
					logging.info("User exists")
					memcache.set(self._memcache_facebook_id, self._user)
					logging.info("%s %s put in memcache"%(self._user.first_name, self._user.last_name))
				else:
					logging.info("User does not exist")
			else:
				logging.info("%s %s already in memcache"%(self._user.first_name, self._user.last_name))
		return self._user
	
	# Put the user
	def put_user(self, facebook_id, facebook_access_token, first_name, last_name, email):
		user = User(
			key_name = str(facebook_id),
			facebook_access_token = str(facebook_access_token),
			first_name = str(first_name),
			last_name = str(last_name),
			email = str(email),
		)
		user.put()
		logging.info("User put in datastore")
		
		memcache.set(self._memcache_facebook_id, user)
		logging.info("User put in memcacche")
		
		# Put the user in the proxy
		self._user = user
		
		return self._user
	
	# Update the facebook user access token
	def update_token(self, facebook_access_token):
		self.user.facebook_access_token = facebook_access_token
		self.user.put()
		logging.info("User access token updated in datastore")
		
		memcache.set(self._memcache_facebook_id, self.user)
		logging.info("User access token updated in memcache")
		
	# Return the user contributions (pages he's admin of)
	@property
	def contributions(self):
		if not hasattr(self, "_contributions"):
			self._contributions = memcache.get(self._memcache_user_contributions_id)
			
			if self._contributions is None:
				graph = facebook.GraphAPI(self.user.facebook_access_token)
				accounts = graph.get_connections(self.user.key().name(),"accounts")["data"]
				
				contributions = []
				if isinstance(accounts, list):
					for account in accounts:
						if(account["category"] != "Application"):
							contribution = {
								"page_name": account["name"],
								"page_id": account["id"],
							}
							contributions.append(contribution)
		
				self._contributions = contributions
				memcache.set(self._memcache_user_contributions_id, self._contributions)
				logging.info("User contributions put in memcache")
			else:
				logging.info("User contributions already in memcache")
		
		return self._contributions
	
	# Tells if a user is an admin of a specific page 
	def is_admin_of(self, page_id):
		for contribution in self.contributions:
			if(contribution["page_id"] == page_id):
				return True
		return False
	
	@property
	def favorites(self):
		step = 20
		
		if not hasattr(self, "_favorites"):
			self._favorites = memcache.get(self._memcache_user_favorites_id)
			if self._favorites is None:
				logging.info("Favorites not in memcache")
				
				q = Favorite.all()
				q.filter("user", self.user.key())
				q.filter("created <", datetime.utcnow())
				q.order("-created")
				favorites = q.fetch(step) # Arbitrary number
				logging.info("Favorites retrieved from datastore")
				
				extended_favorites = Favorite.get_extended_favorites(favorites)
				self._favorites = extended_favorites
				
				memcache.set(self._memcache_user_favorites_id, self._favorites)
				logging.info("Extended favorites put in memcache")
			
			else:
				logging.info("Favorites already in memcache")

		return self._favorites
	
	def get_favorites(self, offset):
		step = 20
		extended_favorites = []
		
		for f in self.favorites:
			if(f["created"] < timegm(offset.utctimetuple())):
				extended_favorites.append(f)

			# If favorites has reached the limit of a "fetching step", stop the loop
			if len(extended_favorites) == step:
				break
		
		# If favorites length is inferior to the size we want, request the datastore
		if(len(extended_favorites) < step):
			q = Favorite.all()
			q.filter("user", self.user.key())
			q.filter("created <", offset)
			q.order("-created")
			favorites = q.fetch(step)
			extended_favorites = Favorite.get_extended_favorites(favorites)
		
			# Add, if any, additional results to memcache
			if(len(extended_favorites) > 0):
				self.favorites += extended_favorites
				memcache.set(self._memcache_user_favorites_id, self.favorites)
				logging.info("New extended favorites put in memcache")
				
		return extended_favorites

	
	@property
	def number_of_favorites(self):
		if not hasattr(self, "_number_of_favorites"):
			shard_name = self._counter_of_favorites_id
			self._number_of_favorites = Shard.get_count(shard_name)
		return self._number_of_favorites
	
	def increment_favorites_counter(self):
		self.add_task("increment")

	def decrement_favorites_counter(self):
		self.add_task("decrement")		
		
	def add_task(self, method):
		task = Task(
			url = "/taskqueue/counter",
			params = {
				"shard_name": self._counter_of_favorites_id,
				"method": method,
			}
		)
		task.add(queue_name = "counters-queue")
		
		
		
