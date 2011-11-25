from google.appengine.ext import db

from user import User

class Influence(db.Model):
	influenced = db.ReferenceProperty(User, required = True, collection_name = "userInfluenced")
	influencer = db.ReferenceProperty(User, required = True, collection_name = "userInfluencer")
	score = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
