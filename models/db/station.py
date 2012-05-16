from google.appengine.ext import db


class Station(db.Model):
	# key_name = facebook_id (page)
	shortname = db.StringProperty(required = True)
	name = db.StringProperty(required = True)
	link = db.StringProperty(required = True) # Link of the facebook page
	created = db.DateTimeProperty(auto_now_add = True)
	updated = db.DateTimeProperty(auto_now = True)
	buffer = db.ListProperty(db.Key)
	timestamp = db.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def get_extended_buffer(buffer):
		"""
			A buffer is a list of keys pointing to tracks entities. This method return a list of dictionnaries formated as such :
				{'youtube_id':id, 'youtube_title': title, 'youtube_duration': duration }
		"""
		return [ {'youtube_id':track.youtube_id, 'youtube_title': track.youtube_title, 'youtube_duration': track.youtube_duration } for track in db.get(buffer)]
