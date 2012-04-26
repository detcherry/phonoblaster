import logging
from datetime import datetime

import django_setup
from django.utils import simplejson as json

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.taskqueue import Task

from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.user import UserApi

from models.db.track import Track
from models.db.broadcast import Broadcast
from models.db.favorite import Favorite


class ApiTracksDeleteHandler(BaseHandler):
	def delete(self):
		cursor = self.request.get("cursor")
		track_id = self.request.get("track_id")
		typeModel = self.request.get("type")
		response = False

		logging.info("In ApiBroadcastsDeleteHandler with track_id :"+str(track_id))

		if(track_id):
			track = Track.get_by_id(int(track_id))
			if(track):
				logging.info("Track found")

				if(typeModel == "broadcast"):
					query = Broadcast.all().filter("track", track).order("expired")
					if(cursor):
						logging.info("Cursor found")
						logging.info(cursor)
						query.with_cursor(start_cursor = cursor)
					broadcasts = query.fetch(1000)
					if(len(broadcasts)>0):
						logging.info("Broadcasts found")
						#filtering broadcast by expired time
						broadcasts_to_delete = []
						countdown = 0
						for b in broadcasts:
							if b.expired < datetime.utcnow():
								broadcasts_to_delete.append(b)

							

						if(len(broadcasts_to_delete) == len(broadcasts)):
							#All broadcasts have to be deleted, we can update cursor
							logging.info("Updating cursor")
							cursor = query.cursor()
						else:
							#Start task later
							countdown = track.youtube_duration

						#Deleting all expired broadcast
						db.delete(broadcasts_to_delete)
						logging.info("Expired broadcasts deleted")

						task = Task(
							method = 'DELETE',
							url = "/taskqueue/deletetrack",
							params = {
								"cursor": cursor,
								"track_id": track_id,
								"type": typeModel,
							},
							countdown = countdown
						)
						task.add(queue_name="worker-queue")
					else:
						task = Task(
							method = 'DELETE',
							url = "/taskqueue/deletetrack",
							params = {
								"track_id": track_id,
								"type": "favorite",
							}
						)
						task.add(queue_name="worker-queue")

				elif (typeModel == "favorite"):
					query = Favorite.all()
					query.filter("track", track.key()) 
					
					if(cursor):
						logging.info("Cursor found")
						logging.info(cursor)
						query.with_cursor(start_cursor = cursor)

					favorite = query.get()

					if favorite is None:
						logging.info("No favorites for this track, deleting track.")
						track.delete()
					else:
						user_proxy = UserApi(favorite.user.key().name())
						user_proxy.decrement_favorites_counter()
						logging.info("User Favorites counter decremented")
						
						Track.decrement_favorites_counter(track.key().id())
						logging.info("Track favorites counter decremented")

						favorite.delete()
						logging.info("Favorite deleted from datastore")

						cursor = query.cursor()

						task = Task(
							method = 'DELETE',
							url = "/taskqueue/deletetrack",
							params = {
								"cursor": cursor,
								"track_id": track_id,
								"type": typeModel,
							}
						)
						task.add(queue_name="worker-queue")

				

				response = True

		else:
			response = False
		self.response.out.write(json.dumps({ "response": response }))

application = webapp.WSGIApplication([
	(r"/taskqueue/deletetrack", ApiTracksDeleteHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()