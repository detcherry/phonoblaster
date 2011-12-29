from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station

class Presence(db.Model):
	# key_name = channel_id
	channel_token = db.StringProperty(required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "presenceStation")
	user = db.ReferenceProperty(User, required = False, collection_name = "presenceUser")
	admin = db.BooleanProperty(default = False)
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
	connected = db.BooleanProperty(default = False)
	ended = db.DateTimeProperty()
	