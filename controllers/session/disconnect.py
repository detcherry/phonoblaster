import logging
import re
from datetime import datetime

import django_setup
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task

from controllers import config

from models.api.station import StationApi
from models.api.user import UserApi

from models.db.session import Session

class DisconnectHandler(webapp.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s cannot receive messages anymore" %(channel_id))
		
		# Init station proxy
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		
		# Decrement the station sessions counter
		station_proxy.decrement_sessions_counter();
		
		session = Session.get_by_key_name(channel_id)
		session.ended = datetime.utcnow()
		session.put()
		logging.info("Session ended in datastore")
		
		# Init user
		user = None
		user_key = Session.user.get_value_for_datastore(session)
		if(user_key):
			user_key_name = user_key.name()
			user_proxy = UserApi(user_key_name)
			user = user_proxy.user
		
		# Add a taskqueue to warn everyone
		extended_session = Session.get_extended_session(session, user)
		
		# Add a taskqueue to warn everyone
		new_session_data = {
			"entity": "session",
			"event": "remove",
			"content": extended_session,
		}
		task = Task(
			url = "/taskqueue/multicast",
			params = {
				"station": config.VERSION + "-" + shortname,
				"data": json.dumps(new_session_data)
			}
		)
		task.add(queue_name="sessions-queue")
		

application = webapp.WSGIApplication([
	(r"/_ah/channel/disconnected/", DisconnectHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()