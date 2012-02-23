import logging
import re
import django_setup
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task

from controllers import config

from models.db.session import Session
from models.db.story import SessionStory

from models.api.station import StationApi
from models.api.user import UserApi

class ConnectHandler(webapp.RequestHandler):
	def post(self):
		channel_id = str(self.request.get('from'))
		logging.info("%s is ready to receive messages" %(channel_id))
		
		session = Session.get_by_key_name(channel_id)
		
		# Init station proxy
		m = re.match(r"(\w+).(\w+)", channel_id)
		shortname = m.group(1)
		station_proxy = StationApi(shortname)
		
		# Init user proxy
		user = None		
		user_key = Session.user.get_value_for_datastore(session)
		if(user_key):
			
			# Load user proxy
			user_key_name = user_key.name()
			user_proxy = UserApi(user_key_name)
			user = user_proxy.user
			
			# Check it there is not already a session story with this session as a parent
			q = SessionStory.all()
			q.ancestor(session.key())
			existing_story = q.get()
			
			if existing_story:
				existing_story.ended = None;
				existing_story.put()
				logging.info("User session. Existing story updated in memcache.")				
			else:
				# Receivers of a session story are the friends of the user and the user himself
				receivers = user_proxy.friends
				receivers.append(user_proxy.user.key())
				
				new_story = SessionStory(
					parent = session,
					receivers = receivers,
					station = station_proxy.station,
				)
				new_story.put()
				logging.info("User session. New session story put in datastore")
			
		else:
			logging.info("Anonymous session. No session story to put in datastore.")
		
		# Increment the station sessions counter
		station_proxy.increment_sessions_counter();
		
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