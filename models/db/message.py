from google.appengine.ext import db

from user import User

class Message(db.Model):
	author = db.ReferenceProperty(User, required = True, collection_name = "messageAuthor")
	host = db.ReferenceProperty(User, required = True, collection_name = "messageHost")
	text = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)