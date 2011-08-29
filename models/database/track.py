from google.appengine.ext import db

class Track(db.Model):
	youtube_title = db.StringProperty()
	youtube_id = db.StringProperty()
	youtube_thumbnail_url = db.LinkProperty()
	youtube_duration = db.IntegerProperty()
	addition_time = db.DateTimeProperty(auto_now_add = True)
	expiration_time = db.DateTimeProperty()
	
	
