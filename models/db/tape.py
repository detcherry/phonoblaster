
from google.appengine.ext import db

from models.db.tracks import Track
from models.db.station import Station



class Tape(db.Model):
	"""
		tape_name - name of the tape.
		tape_thumbnail - thumbnail of the tape
		tracks - list of tracks in tape

	"""

	tape_name = db.StringProperty()
	tape_thumbnail = db.BlobProperty(default = None)
	tracks = db.ListProperty(db.Key)


#class CompilationTrack(db.Model):
#	"""
#		track - reference to the track included in the tape
#	"""
#	tape = db.ReferenceProperty
#	track = db.ReferenceProperty(Tape, collection_name = "compilation_tracks" )
