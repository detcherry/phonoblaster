import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.user import User
from models.db.station import Station

class Comment(db.Model):
	message = db.StringProperty(default ="", required = True)
	user = db.ReferenceProperty(User, required = True, collection_name = "commentUser")
	admin = db.BooleanProperty(default = False, required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "commentStation")
	created = db.DateTimeProperty(auto_now_add = True)