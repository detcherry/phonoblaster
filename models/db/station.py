from google.appengine.ext import db
from google.appengine.ext import blobstore


class Station(db.Model):
	# key_name = facebook_id (page)
	shortname = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	link = db.StringProperty(required = False) # Link of the facebook page
	created = db.DateTimeProperty(auto_now_add=True)
	updated = db.DateTimeProperty(auto_now = True)
	broadcasts = db.ListProperty(db.Key)
	timestamp = db.DateTimeProperty(auto_now_add=True)
	type = db.StringProperty(required=False, choices=set(["user", "page"]))
	full = db.StringProperty() # Link for the full size background
	thumb = db.StringProperty() # Link for the background thumbnail 
	online = db.BooleanProperty() # Online status
	
	
