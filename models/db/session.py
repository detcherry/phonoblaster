from google.appengine.ext import db

from user import User
from station import Station

class Session(db.Model):
	channel_id = db.StringProperty(required = True)
	channel_token = db.StringProperty(required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "sessionStation")
	user = db.ReferenceProperty(User, required = False, collection_name = "sessionUser")
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
	ended = db.DateTimeProperty()