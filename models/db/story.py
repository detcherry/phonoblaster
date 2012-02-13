from google.appengine.ext import db

from models.db.session import Session
from models.db.station import Station

class SessionStory(db.Model):
	# parent = session
	station = db.ReferenceProperty(Station, required = True, collection_name = "sessionStoryStation")
	receivers = db.ListProperty(db.Key, default = None)
	created = db.DateTimeProperty(auto_now_add = True)
	ended = db.DateTimeProperty()
			
		
		