from google.appengine.ext import db

from user import User
from station import Station

class Contribution(db.Model):
	contributor = db.ReferenceProperty(User, required = True, collection_name = "contributionContributor")
	station = db.ReferenceProperty(Station, required = True, collection_name = "contributionStation")
	

