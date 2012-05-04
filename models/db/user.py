from google.appengine.ext import db

class User(db.Model):
	# key_name = uid
    first_name = db.StringProperty(required = True)
    last_name = db.StringProperty(required = True)
    email = db.EmailProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    stations = db.ListProperty(db.Key)
    updated = db.DateTimeProperty(auto_now = True)