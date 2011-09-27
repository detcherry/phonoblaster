from google.appengine.ext import db

from station import Station
from user import User

class Track(db.Model):
	youtube_title = db.StringProperty(required = True)
	youtube_id = db.StringProperty(required = True)
	youtube_thumbnail_url = db.LinkProperty(required = True)
	youtube_duration = db.IntegerProperty(required = True)
	station = db.ReferenceProperty(Station,	required = True, collection_name = "trackStation")
	submitter = db.ReferenceProperty(User, required = True, collection_name = "trackSubmitter")
	added = db.DateTimeProperty(auto_now_add = True)
	expired = db.DateTimeProperty(required = True)
