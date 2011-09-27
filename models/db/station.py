from google.appengine.ext import db
from google.appengine.ext import blobstore

from user import User

class Station(db.Model):
	creator = db.ReferenceProperty(User, required = True, collection_name = "stationCreator")
	identifier = db.StringProperty(required = True)
	picture = blobstore.BlobReferenceProperty(required = True)
	thumbnail = blobstore.BlobReferenceProperty(required = True)
	website = db.StringProperty()
	description = db.StringProperty()
	active = db.DateTimeProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	update = db.DateTimeProperty(auto_now = True)