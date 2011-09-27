from google.appengine.ext import db
from google.appengine.ext import blobstore

from user import User
from station import Station

class Message(db.Model):
	author = db.ReferenceProperty(User, required = True, collection_name = "messageAuthor")
	text = db.StringProperty(required = True)
	station = db.ReferenceProperty(Station, required = True, collection_name = "chattingStation")
	added = db.DateTimeProperty(auto_now_add = True)