from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station

class Comment(db.Model):
	user = db.ReferenceProperty(User, required = True, collection_name = "commentUser")
	station = db.ReferenceProperty(Station, required = True, collection_name = "commentStation")
	content = db.StringProperty(default ="", required = True)
	created = db.DateTimeProperty(auto_now_add = True)