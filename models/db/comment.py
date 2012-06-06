import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station

class Comment(db.Model):
	message = db.StringProperty(default ="", required = True)
	user = db.ReferenceProperty(User, required = True, collection_name = "commentUser")
	admin = db.BooleanProperty(default = False, required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "commentStation")
	created = db.DateTimeProperty(auto_now_add = True)
	
	# TO BE CHANGED
	# Format comments into extended comments
	@staticmethod
	def get_extended_comments(comments, station):
		extended_comments = []
		ordered_extended_comments = []
		
		if(comments):
			
			admin_comments = []
			regular_comments = []
			
			# Dispatch comments in admin and regular
			for c in comments:
				if(c.admin):
					admin_comments.append(c)
				else:
					regular_comments.append(c)
			
			# First we can format admin comments
			for comment in admin_comments:
				extended_comment = Comment.get_extended_comment(comment, station, None)
				extended_comments.append(extended_comment)
			
			# For regular comments, we need to fetch the user
			user_keys = [Comment.user.get_value_for_datastore(c) for c in regular_comments]
			users = db.get(user_keys)
			logging.info("Users retrieved from datastore")
			
			# Then we format the regular comments
			for comment, user in zip(regular_comments, users):
				extended_comment = Comment.get_extended_comment(comment, None, user)
				extended_comments.append(extended_comment)
				
			for c in comments:
				key_name = c.key().name()
				for e in extended_comments:
					if(e["key_name"] == key_name):
						ordered_extended_comments.append(e)
						break
		
		logging.info("Extended comments generated")
		#return extended_comments
		return ordered_extended_comments
	
	# TO BE CHANGED
	# Format a comment and a user into an extended comment entitity
	@staticmethod
	def get_extended_comment(comment, station, user):
		extended_comment = None
		
		# It's not a comment made by an admin
		if(user):
			extended_comment = {
				"key_name": comment.key().name(),
				"message": comment.message,
				"created": timegm(comment.created.utctimetuple()),
				"author_key_name": user.key().name(),
				"author_name": user.first_name + " " + user.last_name,
				"author_url": "/user/" + user.key().name(),
				"admin": comment.admin,
			}
		# The comment has made by an admin
		else:
			extended_comment = {
				"key_name": comment.key().name(),
				"message": comment.message,
				"created": timegm(comment.created.utctimetuple()),
				"author_key_name": station.key().name(),
				"author_name": station.name,
				"author_url": "/" + station.shortname,
				"admin": comment.admin,
			}

		return extended_comment