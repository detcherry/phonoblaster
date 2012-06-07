import logging
from calendar import timegm

from google.appengine.ext import db

from models.db.station import Station

class Message(db.Model):
	message = db.StringProperty(default ="", required = True)
	author = db.ReferenceProperty(User, required = True, collection_name = "commentAuthor")
	host = db.ReferenceProperty(Station, required = True, collection_name = "commentHost")
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
				extended_author = Message.get_extended_message(message, author)
				extended_messages.append(extended_message)
				
			for m in messages:
				key_name = m.key().name()
				for e in extended_messages:
					if(e["key_name"] == key_name):
						ordered_extended_messages.append(e)
						break
		
		logging.info("Extended messages generated")
		#return extended_comments
		return ordered_extended_messages
	
	@staticmethod
	def get_extended_message(message, author):
		extended_message = None
		
		if(author):
			extended_comment = {
				"key_name": message.key().name(),
				"message": message.message,
				"created": timegm(message.created.utctimetuple()),
				"author_key_name": author.key().name(),
				"author_name": author.name,
				"author_url": "/" + author.key().name(),
			}

		return extended_comment