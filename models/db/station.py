from google.appengine.ext import db

class Station(db.Model):
	# key_name = facebook_id (page)
	shortname = db.StringProperty()
	name = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
