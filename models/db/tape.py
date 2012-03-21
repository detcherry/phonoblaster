from google.appengine.ext import db

from models.db.tracks import Track
from models.db.station import Station



class Tape(db.Model):
	"""
		station - station associated to a tape
		tape_name - name of the tape.
		tape_thumbnail - thumbnail of the tape.
		tracks - list of tracks in tape.
		created - time of creation
		updated - time of latest update

	"""

	station = db.ReferenceProperty(Station, required = True, collection_name = "tapesStation")
	tape_name = db.StringProperty()
	tape_thumbnail = db.BlobProperty(default = None) # TODO : BlobProperty / BlobStore, difference?
	tracks = db.ListProperty(db.Key)
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)