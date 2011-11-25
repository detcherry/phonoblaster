from google.appengine.ext import db

from track import Track
from user import User

class Suggestion(db.Model):
	track = db.ReferenceProperty(Track, required = True, collection_name = "trackSuggested")
	recipient = db.ReferenceProperty(User, required = True, collection_name = "suggestionRecipient")
	created = db.DateTimeProperty(auto_now_add = True)
