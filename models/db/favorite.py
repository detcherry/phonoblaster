from google.appengine.ext import db

from track import Track
from user import User

class Favorite(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "trackFavorited")
	user = db.ReferenceProperty(User, required = True, collection_name = "trackFavoriter")
	created = db.DateTimeProperty(auto_now_add = True)