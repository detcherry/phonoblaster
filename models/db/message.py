import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.station import Station

class Message(db.Model):
	message = db.StringProperty()
	youtube_id = db.StringProperty()
	youtube_title = db.StringProperty()
	youtube_duration = db.IntegerProperty()
	soundcloud_id = db.StringProperty()
	soundcloud_title = db.StringProperty()
	soundcloud_duration = db.IntegerProperty()
	soundcloud_thumbnail = db.StringProperty()
	author = db.ReferenceProperty(Station, required = True, collection_name = "messageAuthor")
	host = db.ReferenceProperty(Station, required = True, collection_name = "messageHost")
	created = db.DateTimeProperty(auto_now_add = True)
	
	@staticmethod
	def get_extended_messages(messages, host):
		extended_messages = []
		ordered_extended_messages = []
		
		if(messages):
			# We need to fetch the author
			author_keys = [Message.author.get_value_for_datastore(m) for m in messages]
			authors = db.get(author_keys)
			logging.info("Authors retrieved from datastore")
			
			# Then we format the regular messages
			for message, author in zip(messages, authors):
				extended_message = Message.get_extended_message(message, author)
				extended_messages.append(extended_message)
				
			for m in messages:
				key_name = m.key().name()
				for e in extended_messages:
					if(e["key_name"] == key_name):
						ordered_extended_messages.append(e)
						break
		
		logging.info("Extended messages generated")

		return ordered_extended_messages
	
	@staticmethod
	def get_extended_message(message, author):
		extended_message = None
		
		if(author):
			if(message.message):
				extended_message = {
					"key_name": message.key().name(),
					"text": message.message,
					"type": None,
					"id": None,
					"title": None,
					"duration": None,
					"thumbnail": None,
					"created": timegm(message.created.utctimetuple()),
					"author_key_name": author.key().name(),
					"author_name": author.name,
					"author_url": "/" + author.shortname,
				}
			else:
				extended_message = {
					"key_name": message.key().name(),
					"text": None,
					"created": timegm(message.created.utctimetuple()),
					"track_submitter_key_name": author.key().name(),
					"track_submitter_name": author.name,
					"track_submitter_url": "/" + author.shortname,
				}
				
				if(message.youtube_id):
					extended_message.update({
						"type": "youtube",
						"id": message.youtube_id,
						"title": message.youtube_title,
						"duration": message.youtube_duration,
						"thumbnail": "https://i.ytimg.com/vi/" + message.youtube_id + "/default.jpg",
						"preview": "https://www.youtube.com/embed/" + message.youtube_id + "?autoplay=1",
					})
				else:
					extended_message.update({
						"type": "soundcloud",
						"id": message.soundcloud_id,
						"title": message.soundcloud_title,
						"duration": message.soundcloud_duration,
						"thumbnail": message.soundcloud_thumbnail,
						"preview": "http://player.soundcloud.com/player.swf?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F" + message.soundcloud_id + "&color=3b5998&auto_play=true&show_artwork=false",
					})

		return extended_message