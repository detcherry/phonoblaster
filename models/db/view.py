from google.appengine.ext import db

from models.db.user import User
from models.db.track import Track

class View(db.Model):
	"""
		track - the track the user has viewed
		user - the user that has viewed the track
		
	"""
	
	track = db.ReferenceProperty(Track, required = True, collection_name = "viewTrack")
	user = db.ReferenceProperty(User, required = False, collection_name = "viewUser")
	created = db.DateTimeProperty(auto_now_add = True)
	
	