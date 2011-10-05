import logging

from google.appengine.api import memcache
from models.db.user import User

class InterfaceUser():
	"""
		get_by_facebook_id
		returns: db.Model > User
	"""
	@staticmethod
	def get_by_facebook_id(facebook_id):
		user = memcache.get("user_facebook_"+str(facebook_id))
		if user is not None:
			logging.info("User with facebook_id %s found in memcache" %(str(facebook_id)))
			return user
		else:
			user = User.all().filter("facebook_id", facebook_id).get()
			if user is not None:
				memcache.add("user_facebook_"+str(facebook_id), user)
				logging.info("User with facebook_id %s retrieved from datastore and added to memcache" %(str(facebook_id)))
				return user
			else:
				return None
	
	"""
		put
		returns: db.Model > User
	"""
	@staticmethod
	def put(facebook_id = None, facebook_access_token = None, name = None, first_name = None, last_name = None, email = None):
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
			memcache.add("user_facebook_" + str(facebook_id), user)
			logging.info("User with facebook_id %s put in datastore and memcache" %(str(facebook_id)))
			return user
		else:
			raise ValueError("A user must have at least facebook_id, name, first name and last name")
	
	
	@staticmethod
	def put_email_and_access_token(user, email = None, facebook_access_token = None):
		if email:
			user.email = email
		
		if facebook_access_token:
			user.facebook_access_token = facebook_access_token
		
		user.put()
		memcache.replace("user_facebook_" + str(user.facebook_id), user)
		logging.info("Email and/or access token for user with facebook_id %s added to datastore and memcache" % (str(user.facebook_id)))
		
		return user
		
		
		
		
			