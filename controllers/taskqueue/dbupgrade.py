import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

from models.db.broadcast import Broadcast
from models.db.favorite import Favorite
from models.db.track import Track
from models.db.suggestion import Suggestion
from models.db.air import Air
from models.db.youtube import Youtube
from models.api.station import StationApi

class DBUpgradeHandler(webapp.RequestHandler):
	def post(self):
		dbtype = self.request.get("type")
		logging.info("Upgrading "+dbtype)
		
		if(dbtype):
			cursor = self.request.get("cursor")

			countdown = 0
			#Selecting model depending on type of resquest
			if(dbtype == "track"):
				query = Track.all()
			elif (dbtype == "air"):
				query = Air.all()
			else:
				query = Suggestion.all()
			#Looking for None values
			query.filter("youtube_duration",None)

			#Setting the cursor and the query
			if(cursor):
				logging.info("Cursor found")
				logging.info(cursor)
				query.with_cursor(start_cursor = cursor)

			#retriveing entities
			entities = query.fetch(10)

			if (entities):
				#Initialising list of youtube Ids to retrieve from Youtube using Youtube API
				youtube_ids = []
				entities_to_fetch = []

				for entity in entities:
					if(dbtype == "track"):
						#Fectching all brodcast and favorites that are related to the current track to delete
						queryB = Broadcast.all()
						queryB.filter("track", entity.key())
						while True:
							broadcasts = queryB.fetch(1000)

							if(len(broadcasts) == 0):
								break

							for b in broadcasts:
								b.delete()

						queryT = Favorite.all()
						queryT.filter("track = ", entity)
						while True:
							favorites = queryT.fetch(1000)

							if(len(favorites) == 0):
								break

							for f in favorites:
								f.delete()


					logging.info("Deleting entity with Youtube ID : "+entity.youtube_id)
					entity.delete()

				cursor = query.cursor()
				task = Task(
						url = "/taskqueue/upgrade",
						params = {'cursor':cursor,'type':dbtype},
						countdown = 1 ,
					)
				task.add(queue_name = "upgrade-queue")
				logging.info("Task Upgrade put in the queue")

			else:
				logging.info("No tracks found")
				task = Task(
					url = "/taskqueue/mail",
					params = {
						"to": "ahmed@phonoblaster.com",
						"subject": "["+dbtype+"] Upgrade",
						"body": "Upgrade Done",
					}
				)
				task.add(queue_name = "worker-queue")


application = webapp.WSGIApplication([
	(r"/taskqueue/upgrade", DBUpgradeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	