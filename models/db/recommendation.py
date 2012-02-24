from google.appengine.ext import db

from models.db.user import User

class Recommendation(db.Model):
	youtube_id = db.StringProperty(required = True)
	user = db.ReferenceProperty(User, required = True, collection_name = "recommandationUser")
	created = db.DateTimeProperty(auto_now_add = True)