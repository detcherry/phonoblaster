from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station

class Presence(db.Model):
	# key_name = channel_id
	channel_token = db.StringProperty(required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "presenceStation")
	user = db.ReferenceProperty(User, required = False, collection_name = "presenceUser")
	admin = db.BooleanProperty(default = False, required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
	connected = db.BooleanProperty(default = False)
	ended = db.DateTimeProperty()
	
	# Format presences into extended presences
	@staticmethod
	def get_extended_presences(presences, station):
		extended_presences = []
		
		admins_presences = []
		authenticated_presences = []
		unauthenticated_presences = []
		
		user_keys = []
		
		# Dispatch admin, authenticated and unauthenticated presences
		for p in presences:
			if(p.admin):
				admins_presences.append(p)
			else:
				user_key = Presence.user.get_value_for_datastore(p)
				if user_key:
					authenticated_presences.append(p)
					user_keys.append(user_key)
				else:
					unauthenticated_presences.append(p)
		
		# Add the extended presences for admins
		for presence in admins_presences:
			extended_presence = Presence.get_extended_presence(presence, station, None)
			extended_presences.append(extended_presence)
		
		# Retrieve users of authenticated presences
		users = db.get(user_keys)
		
		# Add the extended presences for authenticated users
		for presence, user in zip(authenticated_presences, users):
			extended_presence = Presence.get_extended_presence(presence, station, user)
			extended_presences.append(extended_presence)
		
		# Add the extended presences for unauthenticated users
		for presence in unauthenticated_presences:
			extended_presence = Presence.get_extended_presence(presence, station, None)
			extended_presences.append(extended_presence)
			
		return extended_presences
	
	# Format a presence into an extended presence
	@staticmethod
	def get_extended_presence(presence, station, user):
		extended_presence = None
		
		# If admin
		if(presence.admin):
			extended_presence = {
				"channel_id": presence.key().name(),
				"created": timegm(presence.created.utctimetuple()),
				"listener_key_name": station.key().name(),
				"listener_name": station.name,
				"listener_url": "/"+ station.shortname,
				"admin": True,
			}
		else:
			# If there is a user, that means it's an authenticated presence
			if(user):
				extended_presence = {
					"channel_id": presence.key().name(),
					"created": timegm(presence.created.utctimetuple()),
					"listener_key_name": user.key().name(),
					"listener_name": user.first_name + " " + user.last_name,
					"listener_url": "/user/" + user.key().name(),
					"admin": False,
				}
			else:
				extended_presence = {
					"channel_id": presence.key().name(),
					"created": timegm(presence.created.utctimetuple()),
					"user_key_name": None,
					"user_name": None,
					"listener_url": None,
					"admin": False,
				}
		
		return extended_presence
		
	