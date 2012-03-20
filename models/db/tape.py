
from google.appengine.ext import db

from models.db.tracks import Track
from models.db.station import Station



class Tape(db.Model):
	"""
		tape_name - name of the tape.

	"""

	tape_name = db.StringProperty()


class CompilationTrack(db.Model):
	"""
		track - reference to the track included in the tape
	"""
	
	track = db.ReferenceProperty(Tape, collection_name = "compilation_tracks" )
