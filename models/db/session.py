from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station

class Session(db.Model):
	# key_name = channel_id
	channel_token = db.StringProperty(required = True)
	user = db.ReferenceProperty(User, required = False, collection_name = "sessionUser")
	station = db.ReferenceProperty(Station, required = True, collection_name = "sessionStation")
	created = db.DateTimeProperty(auto_now_add = True)
	ended = db.DateTimeProperty()
	
	@staticmethod
	def get_extended_sessions(sessions):		
		user_keys = []
		users = []
		user_sessions = []
		
		anonymous_users = []
		anonymous_sessions = []
		
		for s in sessions:
			user_key = Session.user.get_value_for_datastore(s)
			if user_key is not None:
				user_keys.append(user_key)
				user_sessions.append(s)
			else:
				anonymous_users.append(None)
				anonymous_sessions.append(s)
		
		users = db.get(user_keys)
		
		user_extended_sessions = [Session.get_extended_session(s, u) for s, u in zip(user_sessions, users)]
		anonymous_extended_sessions = [Session.get_extended_session(s, au) for s, au in zip(anonymous_sessions, anonymous_users)]
		extended_sessions = user_extended_sessions + anonymous_extended_sessions
		
		return extended_sessions
	
	@staticmethod
	def get_extended_session(session, user):
		if(user):	
			extended_session = {
				"key_name": session.key().name(),
				"created": timegm(session.created.utctimetuple()),
				"listener_key_name": user.key().name(),
				"listener_name": user.first_name + " " + user.last_name,
				"listener_url": "/user/" + user.key().name(),
			}
		else:
			extended_session = {
				"key_name": session.key().name(),
				"created": timegm(session.created.utctimetuple()),
				"listener_key_name": None,
				"listener_name": None,
				"listener_url": None,
			}
			
		return extended_session

