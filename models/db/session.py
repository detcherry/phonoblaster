from calendar import timegm

from google.appengine.ext import db

from models.db.station import Station

class Session(db.Model):
	# key_name = channel_id
	channel_token = db.StringProperty(required = True)
	listener = db.ReferenceProperty(Station, required = False, collection_name = "sessionListener")
	host = db.ReferenceProperty(Station, required = True, collection_name = "sessionHost")
	created = db.DateTimeProperty(auto_now_add = True)
	ended = db.DateTimeProperty()
	
	@staticmethod
	def get_extended_sessions(sessions):		
		listeners_keys = []
		listeners = []
		listener_sessions = []
		
		anonymous_listeners = []
		anonymous_sessions = []
		
		for s in sessions:
			listener_key = Session.listener.get_value_for_datastore(s)
			if listener_key is not None:
				listeners_keys.append(listener_key)
				listener_sessions.append(s)
			else:
				anonymous_listeners.append(None)
				anonymous_sessions.append(s)
		
		listeners = db.get(listeners_keys)
		
		listener_extended_sessions = [Session.get_extended_session(s, l) for s, l in zip(listener_sessions, listeners)]
		anonymous_extended_sessions = [Session.get_extended_session(s, al) for s, al in zip(anonymous_sessions, anonymous_listeners)]
		extended_sessions = listener_extended_sessions + anonymous_extended_sessions
		
		return extended_sessions
	
	@staticmethod
	def get_extended_session(session, listener):
		if(listener):	
			extended_session = {
				"key_name": session.key().name(),
				"created": timegm(session.created.utctimetuple()),
				"listener_key_name": listener.key().name(),
				"listener_name": listener.name,
				"listener_url": "/" + listener.shortname,
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

