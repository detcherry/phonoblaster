from google.appengine.ext import db

class User(db.Model):
	# key_name = facebook_id
    facebook_access_token = db.StringProperty(required = True)
    first_name = db.StringProperty(required = True)
    last_name = db.StringProperty(required = True)
    email = db.EmailProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    updated = db.DateTimeProperty(auto_now = True)