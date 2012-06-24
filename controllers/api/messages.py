import logging
import json
from datetime import datetime
from datetime import timedelta

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
		logging.info(message)
		shortname = self.request.get("shortname")
		
		host_proxy = StationApi(shortname)
		self.host = host_proxy.station
		
		if(self.user_proxy.profile):
			
			author_key = db.Key.from_path("Station", self.user_proxy.profile["key_name"])
			author = db.get(author_key)
			
			if(message["text"]):
				text = message["text"][:500].replace("\n"," ")
			else:
				text = None
				
			new_message = Message(
				key_name = message["key_name"],
				message = text,
				youtube_id = message["youtube_id"],
				youtube_title = message["youtube_title"],
				youtube_duration = message["youtube_duration"],
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
