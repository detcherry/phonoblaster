import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

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
			time = self.request.get("time")

			processData = False
			countdown = 0
			#Selecting model depending on type of resquest
			if(dbtype == "track"):
				query = Track.all()
			elif (dbtype == "air"):
				query = Air.all()
			else:
				query = Suggestion.all()
			#Ordering by date, old to recent
			query.order("-created")

			#Setting the cursor and the query
			if(cursor and time):
				logging.info("Cursor found")
				logging.info(cursor)
				#Filtering recent entities because they are up to date
				query.filter("created < ", time)
				query.with_cursor(start_cursor = cursor)
				processData = True
			elif ((not cursor) and (not time)):
				logging.info("No Cursor, Creating the query to fetch entities")
				time = datetime.now()
				logging.info(time)
				#Filtering recent entities because they are up to date
				query.filter("created < ", time)
				processData = True

			#if the cursor was successfully set, start processing
			if(processData):
				#retriveing entities
				entities = query.fetch(10)

				if (entities):
					#Initialising list of youtube Ids to retrieve from Youtube using Youtube API
					youtube_ids = []
					entities_to_fetch = []

					for entity in entities:
						if((not entity.youtube_duration) or (not entity.youtube_title)):
							#Adding entity to entities that have to be completeed by accessing youtube and retriving information
							youtube_ids.append(entity.youtube_id)
							entities_to_fetch.append(entity)
						else:
							logging.info("Entity with Youtube id "+entity.youtube_id+" is up to date!")
							
					#Initialising list of extended tracks retrieved from youtube
					extended_tracks = []

					if(len(youtube_ids) > 0):
						try:
							extended_tracks = Youtube.get_extended_tracks_upgrade(youtube_ids)
						except Exception, e:
							#If a problem occured, we skip the current batch
							logging.error(''.join(traceback.format_exception(*sys.exc_info())))
							cursor = query.cursor()

						success = True

						#Iterating over elements
						for i in range(len(extended_tracks)):
							logging.info("Youtube id : "+extended_tracks[i]["id"])
							extended_track = extended_tracks[i]
							entity = entities_to_fetch[i]


							if(extended_track["code"] == '200'):
								#Everything is OK, Youtube API access executed properly
								logging.info("Track successfully retrived from Youtube")
								youtube_duration = int(extended_track["duration"])
								youtube_title = extended_track["title"]

								try:
									entity.youtube_duration = youtube_duration
									entity.youtube_title = youtube_title
									entity.put()
									logging.debug(entity)
									logging.debug(entity.youtube_duration)
									logging.debug(entity.youtube_title)
									logging.info("Entity put in datastore (without need to decode)")
								except Exception, e:
									logging.error(''.join(traceback.format_exception(*sys.exc_info())))
									entity.youtube_duration = youtube_duration
									entity.youtube_title = youtube_title.decode("utf-8")
									entity.put()
									logging.info("Entity put in datastore")

							elif (extended_track["code"] == '403'):
								#Problem, to many queries, need to wait a bit to avoid quota limitation
								logging.info("Youtube API quota limitation")
								countdown = 5*60 # Wait 10 minutes before executing next element in queue
								success = False
								break
							elif (extended_track["code"] == '404'):
								#Track removed from Youtube
								logging.info("Track removed from Youtube")

								entity.youtube_duration = None
								entity.youtube_title = None
								entity.put()
							else:
								logging.info("Problem with track")
								#Other problem, we skip the entity
								cursor = query.cursor()
								success = False
								break

						if(success):
							cursor = query.cursor()

							
					else:
						cursor = query.cursor()
						logging.info("All entities are Up to Date.")
					
					task = Task(
							url = "/taskqueue/upgrade",
							params = {'cursor':cursor, 'time':time, 'type':dbtype},
							countdown = countdown +1 ,
						)
					task.add(queue_name = "upgrade-queue")
					logging.info("Task Upgrade put in the queue, with a delai of "+str(countdown/60)+" minutes and 1 seconde")

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