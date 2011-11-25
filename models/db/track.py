from google.appengine.ext import db

from user import User

class Track(db.Model):
	youtube_id = db.StringProperty(required = True)
	youtube_title = db.StringProperty(required = True)
	youtube_thumbnail_url = db.LinkProperty(required = True)
	youtube_duration = db.IntegerProperty(required = True)
	user = db.ReferenceProperty(User, required = True, collection_name = "trackSubmitter")
	created = db.DateTimeProperty(auto_now_add = True)
	