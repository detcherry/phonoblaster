from google.appengine.ext import db

class User(db.Model):
    facebook_id = db.StringProperty(required = True)
    facebook_access_token = db.StringProperty()
    name = db.StringProperty(required = True)
    first_name = db.StringProperty(required = True)
    last_name = db.StringProperty(required = True)
    public_name = db.StringProperty()
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    updated = db.DateTimeProperty(auto_now = True)


