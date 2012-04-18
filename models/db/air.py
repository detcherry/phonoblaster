from google.appengine.ext import db

from models.db.station import Station
from models.db.track import Track

class Air(db.Model):
	# key_name = station.key().name()	
	shortname = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	link = db.StringProperty(required = True)
	youtube_id = db.StringProperty(required = True)
	youtube_title = db.StringProperty()
	youtube_duration = db.IntegerProperty()
	expired = db.DateTimeProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	