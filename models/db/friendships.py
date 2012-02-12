from google.appengine.ext import db

class Friendships(db.Model):
	# parent = user
	friends = db.ListProperty(db.Key, default = None)