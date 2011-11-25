from google.appengine.ext import db

from track import Track
from user import User

class Broadcast(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "trackBroadcast")
	broadcaster = db.ReferenceProperty(User, required = True, collection_name = "trackBroadcaster")
	expired = db.DateTimeProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
