from google.appengine.ext import db


class Station(db.Model):
	# key_name = facebook_id (page)
	shortname = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	link = db.StringProperty(required = True) # Link of the facebook page
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
	broadcasts = db.StringListProperty()
	timestamp = db.DateTimeProperty(auto_now_add=True)
