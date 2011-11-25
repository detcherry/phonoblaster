from google.appengine.ext import db

from user import User

class Session(db.Model):
	channel_id = db.StringProperty(required = True)
	channel_token = db.StringProperty(required = True)
	broadcaster = db.ReferenceProperty(User, required = True, collection_name = "sessionBroadcaster")
	listener = db.ReferenceProperty(User, required = False, collection_name = "sessionListener")
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
	confirmed = db.DateTimeProperty()
	ended = db.DateTimeProperty()