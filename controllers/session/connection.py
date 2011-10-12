import logging
from datetime import datetime
from datetime import timedelta
from calendar import timegm
from django.utils import simplejson

from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.db.track import Track
from models.db.session import Session
from models.db.station import Station
from models.db.message import Message
from models.queue import Queue

from google.appengine.api.labs.taskqueue import Task

class ChannelConnectionHandler(webapp.RequestHandler):
	def post(self):
		channel_id = self.request.get('from')
		logging.info("%s is ready to receive messages" %(channel_id))
		
		#We extract the session
		session = Session.all().filter("channel_id", channel_id).get()
		station = session.station
		logging.info("Listening to the station %s" %(station.identifier))
		
		#We get the current playlist
		queue = Queue(station.key())
		#tracklist = queue.getTracks()
		tracklist = queue.get_tracks()

		tracklist_init_output = []
		if(tracklist):
			# Get the submitters in one trip to the datastore
			user_keys = [Track.submitter.get_value_for_datastore(t) for t in tracklist]
			submitters = db.get(user_keys)
			tracks = zip(tracklist, submitters)
						
			for track in tracks:
				tracklist_init_output.append({
					"phonoblaster_id": str(track[0].key().id()),
					"title":track[0].youtube_title,
					"id": track[0].youtube_id,
					"thumbnail": track[0].youtube_thumbnail_url,
					"duration":track[0].youtube_duration,
					"submitter_id":track[1].key().id(),
					"submitter_fcbk_id":track[1].facebook_id,
					"added": timegm(track[0].added.utctimetuple()),
					"expired": timegm(track[0].expired.utctimetuple()),
				})

		#We format a message and send it to the client
		tracklist_init_data = {
			"type": "tracklist_init",
			"content": tracklist_init_output,
		}		
		channel.send_message(channel_id, simplejson.dumps(tracklist_init_data))
		logging.info("Tracklist sent")
		
		#We get the 10 last messages (from the last 3 minutes)
		query = Message.all()
		query.filter("station", station.key())
		query.filter("added >", datetime.now() - timedelta(0,180))
		messages = query.fetch(10)
		
		chat_init_output = []
		if(messages):
			# Get the authors in one trip to the datastore
			user_keys = [Message.author.get_value_for_datastore(m) for m in messages]
			authors = db.get(user_keys)
			ims = zip(messages, authors)
			for im in ims:
				chat_init_output.append({
						"text": im[0].text,
						"author_id": im[1].key().id(),
						"author_public_name": im[1].public_name,
						"author_fcbk_id": im[1].facebook_id,
						"added": timegm(im[0].added.utctimetuple()),
				})

		#We format a message and send it to the client
		chat_init_data = {
			"type":"chat_init",
			"content": chat_init_output,
		}
		channel.send_message(channel_id, simplejson.dumps(chat_init_data))
		logging.info("Latest messages sent")
		
		# Inform everyone a new listener has arrived
		listener_new_data = {
			"type":"listener_new",
			"content": [],
		}
		excluded_channel_id = channel_id
		task = Task(
			url = "/taskqueue/notify",
			params = { 
				"station_key": str(station.key()),
				"data": simplejson.dumps(listener_new_data),
				"excluded_channel_id": excluded_channel_id,
			},
		)
		task.add(
			queue_name = "listener-queue-1"
		)
		
		# Retrieve the number of active sessions
		q = Session.all()
		q.filter("station", station.key())
		q.filter("ended", None)
		q.filter("created >", datetime.now() - timedelta(0,7200))
		nb_of_listeners = q.count()
		
		listener_init_data = {
			"type":"listener_init",
			"content": nb_of_listeners,
		}
		channel.send_message(channel_id, simplejson.dumps(listener_init_data))
		logging.info("New listener got the number of listeners")

application = webapp.WSGIApplication([
	(r"/_ah/channel/connected/", ChannelConnectionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()