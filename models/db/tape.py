import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.track import Track
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
	tape_name = db.StringProperty(required = True)
	tape_thumbnail = db.BlobProperty(default = None) # TODO : BlobProperty / BlobStore, difference?
	tracks = db.ListProperty(db.Key)
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)



	@staticmethod
	def get_extended_tape(tape):
		track_keys = None
		tracks = None
		extended_tracks = None

		track_keys = Tape.tracks.get_value_for_datastore(tape)
		logging.info("Tracks retrieved from datastore")
		tracks = db.get(track_keys)
		extended_tracks = Track.get_extended_tracks(tracks)
		logging.info("Extended tracks generated from Youtube")
		
		extended_tape = None

		extended_tape = {
			"key_name": tape.key().id_or_name(),
			"tape_name": tape.tape_name,
			"created": timegm(tape.created.utctimetuple()),
			"extended_tracks": extended_tracks,
		}

		return extended_tape