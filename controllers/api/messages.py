import logging
from datetime import datetime
from datetime import timedelta
import django_setup
from django.utils import simplejson as json

from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi
from models.db.message import Message

class ApiMessagesHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		host_proxy = StationApi(shortname)
		host = host_proxy.station
		
		if(host):
			q = Message.all()
			q.filter("host", host.key())
			q.filter("created <", datetime.utcnow())
			q.order("-created")
			messages = q.fetch(50) # Arbitrary number
	
			extended_messages = Message.get_extended_messages(messages, host)
			self.response.out.write(json.dumps(extended_messages))
		else:
			self.error(404)

	@login_required
	def post(self):
		message = json.loads(self.request.get("content"))
		shortname = self.request.get("shortname")
		
		host_proxy = StationApi(shortname)
		self.host = host_proxy.station
		
		self.user = self.user_proxy.user

		author_key_name = message["author_key_name"]
		
		# Check if the user is the author
		if(self.user_proxy.is_admin_of(author_key_name)):
			# Building author db key
			author_key = db.Key_from_path("Station", author_key_name )
			author = db.get(author_key)
			# Put the new message to the datastore
			new_message = Message(
				key_name = message["key_name"],
				message = message["message"][:500].replace("\n"," "),
				host = self.host.key(),
				author = author_key,
			)
			new_message.put()
			logging.info("New message put to the datastore")
			
			extended_message = Message.get_extended_message(new_message, author)
			
			# Add a taskqueue to warn everyone
			new_message_data = {
				"entity": "message",
				"event": "new",
				"content": extended_message,
			}
			task = Task(
				url = "/taskqueue/multicast",
				params = {
					"station": config.VERSION + "-" + shortname,
					"data": json.dumps(new_message_data)
				}
			)
			task.add(queue_name="messages-queue")
			self.response.out.write(json.dumps({ "response": True }))
		else:
			self.response.out.write(json.dumps({ "response": False }))