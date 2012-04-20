import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from models.db.track import Track
from models.db.suggestion import Suggestion
from models.db.youtube import Youtube
from models.api.station import StationApi
from google.appengine.api.taskqueue import Task

class DBUpgradeHandler(webapp.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")
		time = self.request.get("time")

		processData = False
		countdown = 0
		query = Track.all()
		query.order("-created")

		#Setting the cursor and the query
		if(cursor and time):
			logging.info("Cursor found")
			logging.info(cursor)
			query.filter("created < ", time)
			query.with_cursor(start_cursor = cursor)
			processData = True
		elif ((not cursor) and (not time)):
			logging.info("No Cursor, Creating the query to fetch tracks")
			time = datetime.now()
			logging.info(time)
			query.filter("created < ", time)
			processData = True

		#if the cursor was successfully set, start processing
		if(processData):
			#retriveing tracks
			tracks = query.fetch(10)

			if (tracks):
				#Initialising list of youtube Ids to retrieve from Youtube using Youtube API
				youtube_ids = []
				tracks_to_fetch = []

				for track in tracks:
					if((not track.youtube_duration) or (not track.youtube_title)):
						#Adding track to tracks that have to be completeed by accessing youtube and retriving information
						youtube_ids.append(track.youtube_id)
						tracks_to_fetch.append(track)
					else:
						logging.info("Track with Youtube id "+track.youtube_id+" is up to date!")

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
						extended_track = extended_tracks[i]
						track = tracks_to_fetch[i]


						if(extended_track["code"] == '200'):
							#Everything is OK, Youtube API access executed properly
							logging.info("Track successfully retrived from Youtube")
							youtube_duration = int(extended_track["duration"])
							youtube_title = extended_track["title"]

							track.youtube_duration = youtube_duration
							track.youtube_title = youtube_title.decode("utf-8")
							track.put()

						elif (extended_track["code"] == '403'):
							#Problem, to many queries, need to wait a bit to avoid quota limitation
							logging.info("Youtube API quota limitation")
							countdown = 5*60 # Wait 10 minutes before executing next element in queue
							success = False
							break
						elif (extended_track["code"] == '404'):
							#Track removed from Youtube
							logging.info("Track removed from Youtube")

							track.youtube_duration = None
							track.youtube_title = None
							track.put()
						else:
							#Other problem, we skip the track
							cursor = query.cursor()
							success = False
							break

					if(success):
						cursor = query.cursor()

						
				else:
					cursor = query.cursor()
					logging.info("All tracks are Up to Date.")
				
				task = Task(
						url = "/taskqueue/upgrade",
						params = {'cursor':cursor, 'time':time},
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
						"subject": "Upgrade",
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