from google.appengine.ext import db
from models.db.station import Station

class User(db.Model):
	# key_name = uid
    first_name = db.StringProperty(required = True)
    last_name = db.StringProperty(required = True)
    email = db.EmailProperty(required = True)
    stations = db.ListProperty(db.Key)
    profile = db.ReferenceProperty(Station, required = False, collection_name = "userProfile")
    created = db.DateTimeProperty(auto_now_add = True)
    updated = db.DateTimeProperty(auto_now = True)