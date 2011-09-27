from google.appengine.ext import db

from user import User
from station import Station

class FcbkRequest(db.Model):
	fcbk_id = db.StringProperty(required = True)
	requester = db.ReferenceProperty(User, required = True, collection_name = "requestSender")
	station = db.ReferenceProperty(Station, required = True, collection_name = "requestStation")
	created = db.DateTimeProperty(auto_now_add = True)
