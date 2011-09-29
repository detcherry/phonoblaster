import logging
from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.db.session import Session
from models.db.station import Station
from models.db.message import Message
from models.queue import Queue

class ChannelConnectionHandler(webapp.RequestHandler):
	def post(self):
		channel_id = self.request.get('from')
		logging.info("%s is ready to receive messages" %(channel_id))
		
		#We extract the session
		session = Session.all().filter("channel_id", channel_id).get()
		station = session.station
		
		#We get the current playlist
		queue = Queue(station.key())
		tracklist = queue.getTracks()
		tracklist_init_output = []
		if(tracklist):
			for track in tracklist:
				tracklist_init_output.append({
					"phonoblaster_id": str(track.key().id()),
					"title":track.youtube_title,
					"id": track.youtube_id,
					"thumbnail": track.youtube_thumbnail_url,
					"duration":track.youtube_duration,
					"submitter_id":track.submitter.key().id(),
					"submitter_fcbk_id":track.submitter.facebook_id,
					"added": timegm(track.added.utctimetuple()),
					"expired": timegm(track.expired.utctimetuple()),
				})
		#We format a message and send it to the client
		tracklist_init_data = {
			"type": "tracklist_init",
			"content": tracklist_init_output,
		}		
		channel.send_message(channel_id, simplejson.dumps(tracklist_init_data))
		
		#We get the 10 last messages (from the last 3 minutes)
		query = Message.all()
		query.filter("station", station.key())
		query.filter("added >", datetime.now() - timedelta(0,180))
		messages = query.fetch(10)
		chat_init_output = []
		if(messages):
			for message in messages:
				chat_init_output.append({
					"text": message.text,
					"author_id": message.author.key().id(),
					"author_public_name": message.author.public_name,
					"author_fcbk_id": message.author.facebook_id,
					"added": timegm(message.added.utctimetuple()),
				})
		#We format a message and send it to the client
		chat_init_data = {
			"type":"chat_init",
			"content": chat_init_output,
		}
		channel.send_message(channel_id, simplejson.dumps(chat_init_data))
		
		#Lastly we are going to inform everyone that a new listener has arrived
		q = Session.all()
		q.filter("station", station.key())
		q.filter("ended", None)
		listening_sessions = q.filter("created >", datetime.now() - timedelta(0,7200))
		
		number_of_listeners = 0
		for session in listening_sessions:
			number_of_listeners += 1
			if(session.channel_id != channel_id):
				listener_new_data = {
					"type":"listener_new",
					"content": [],
				}
				channel.send_message(session.channel_id, simplejson.dumps(listener_new_data))

		listener_init_data = {
			"type":"listener_init",
			"content": number_of_listeners,
		}
		channel.send_message(channel_id, simplejson.dumps(listener_init_data))

application = webapp.WSGIApplication([
	(r"/_ah/channel/connected/", ChannelConnectionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()