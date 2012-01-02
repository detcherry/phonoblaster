import logging
from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi
from models.db.comment import Comment

class ApiCommentsHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		self.station = station_proxy.station
		self.response.out.write(json.dumps(self.comments))

	@login_required
	def post(self):
		key_name = self.request.get("key_name")
		content = self.request.get("content")
		shortname = self.request.get("shortname")
		
		# Check if the user is an admin
		station_proxy = StationApi(shortname)
		self.station = station_proxy.station
		
		self.user = self.user_proxy.user
		
		admin = False
		if(self.user_proxy.is_admin_of(self.station.key().name())):
			admin = True
		
		# Put the new comment to the datastore
		new_comment = Comment(
			key_name = key_name,
			content = content,
			station = self.station.key(),
			user = self.user.key(),
			admin = admin
		)
		new_comment.put()
		logging.info("New comment put to the datastore")
		
		# Get the extended comment
		extended_comment = self.get_extended_comment(new_comment, self.station, self.user)
		
		# Add a taskqueue to warn everyone
		new_comment_data = {
			"event": "new-comment",
			"content": extended_comment,
		}
		task = Task(
			url = "/taskqueue/multicast",
			params = {
				"station": config.VERSION + "-" + shortname,
				"data": json.dumps(new_comment_data)
			}
		)
		task.add(queue_name="comments-queue")
		self.response.out.write(json.dumps({ "response": True }))
	
	# Returns the latest comments (from the last 3 minutes)
	@property
	def comments(self):
		if not hasattr(self, "_comments"):
			q = Comment.all()
			q.filter("station", self.station.key())
			q.filter("created >", datetime.utcnow() - timedelta(0,180))
			q.order("created")
			comments = q.fetch(50) # Arbitrary number

			# Format extended comments
			self._comments = self.get_extended_comments(self.station, comments)
		return self._comments
	
	# Format comments into extended comments
	def get_extended_comments(self, station, comments):
		extended_comments = []
		
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
				extended_comment = self.get_extended_comment(comment, station, None)
				extended_comments.append(extended_comment)
			
			# For regular comments, we need to fetch the user
			user_keys = [Comment.user.get_value_for_datastore(c) for c in regular_comments]
			users = db.get(user_keys)
			
			# Then we format the regular comments
			for comment, user in zip(regular_comments, users):
				extended_comment = self.get_extended_comment(comment, station, user)
				extended_comments.append(extended_comment)

		return extended_comments
	
	# Format a comment and a user into an extended comment entitity
	def get_extended_comment(self, comment, station, user):
		extended_comment = None
		
		if(comment.admin):
			extended_comment = {
				"key_name": comment.key().name(),
				"content": comment.content,
				"created": timegm(comment.created.utctimetuple()),
				"author_key_name": station.key().name(),
				"author_name": station.name,
				"author_url": "/" + station.shortname,
				"admin": comment.admin,
			}
		
		else:
			extended_comment = {
				"key_name": comment.key().name(),
				"content": comment.content,
				"created": timegm(comment.created.utctimetuple()),
				"author_key_name": user.key().name(),
				"author_name": user.first_name + " " + user.last_name,
				"author_url": "/user/" + user.key().name(),
				"admin": comment.admin,
			}

		return extended_comment