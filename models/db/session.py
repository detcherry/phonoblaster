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
		# Filter only sessions that have a user
		keys = [Session.user.get_value_for_datastore(s) for s in sessions]
		
		user_keys = []
		none_keys = []
		for key in keys:
			if key is not None:
				user_keys.append(key)
			else:
				none_keys.append(key)
				
		users = User.get(user_keys)
		
		user_sessions = []
		for s in sessions:
			session_user_key = Session.user.get_value_for_datastore(s)
			for u in users:
				if u.key() == session_user_key:
					user_sessions.append(s)
					break
		
		extended_sessions = [Session.get_extended_session(s, u) for s, u in zip(user_sessions, users)]
		
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

