from google.appengine.ext import db

from models.db.user import User
from models.db.track import Track


class Favorite(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "favoriteTrack")
	user = db.ReferenceProperty(User, required = True, collection_name = "favoriteUser")
	created = db.DateTimeProperty(auto_now_add = True)