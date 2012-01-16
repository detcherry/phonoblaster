import logging
from datetime import datetime
from datetime import timedelta
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
		
		q = Comment.all()
		q.filter("station", self.station.key())
		q.filter("created >", datetime.utcnow() - timedelta(0,180))
		q.order("created")
		comments = q.fetch(50) # Arbitrary number
		
		extended_comments = Comment.get_extended_comments(comments, self.station)
		
		self.response.out.write(json.dumps(extended_comments))

	@login_required
	def post(self):
		#key_name = self.request.get("key_name")
		#content = self.request.get("content")
		comment = json.loads(self.request.get("content"))
		logging.info(comment);
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
			key_name = comment["key_name"],
			message = comment["message"],
			station = self.station.key(),
			user = self.user.key(),
			admin = admin
		)
		new_comment.put()
		logging.info("New comment put to the datastore")
		
		if(admin):
			extended_comment = Comment.get_extended_comment(new_comment, self.station, None)
		else:
			extended_comment = Comment.get_extended_comment(new_comment, None, self.user)
		
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