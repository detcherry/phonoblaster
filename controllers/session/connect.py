import logging
import re
import django_setup
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task

from controllers import config

from models.db.session import Session

from models.api.station import StationApi
from models.api.user import UserApi

class ConnectHandler(webapp.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s is ready to receive messages" %(channel_id))
		
		# Init station proxy
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		
		# Increment the station sessions counter
		station_proxy.increment_sessions_counter();
		
		# Get session
		session = Session.get_by_key_name(channel_id)
		# After a reconnection the session may have ended. Correct it.
		if session.ended is not None:
			session.ended = None
			session.put()
			logging.info("Session had ended (probable reconnection). Corrected session put.")

		# Init user
		user = None
		user_key = Session.user.get_value_for_datastore(session)
		if(user_key):
			# Load user proxy
			user_key_name = user_key.name()
			user_proxy = UserApi(user_key_name)
			user = user_proxy.user
		
		# Add a taskqueue to warn everyone
		extended_session = Session.get_extended_session(session, user)
		
		# Add a taskqueue to warn everyone
		new_session_data = {
			"entity": "session",
			"event": "new",
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
	(r"/_ah/channel/connected/", ConnectHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()