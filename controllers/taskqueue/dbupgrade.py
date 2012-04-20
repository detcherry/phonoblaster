import logging

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

		if(processData):
			tracks = query.fetch(100)

			if (tracks):
				for track in tracks:
					logging.info("Track Youtube id : "+track.youtube_id)

					if((not track.youtube_duration) or (not track.youtube_title)):
						logging.info("Youtube API Call is necessary")
						try:
							extended_track = Youtube.get_extended_track(track.youtube_id)
							
							if(extended_track["code"] == '200'):
								#Everything is OK, Youtube API access executed properly
								youtube_duration = int(extended_track["duration"])
								youtube_title = extended_track["title"]

								track.youtube_duration = youtube_duration
								track.youtube_title = youtube_title.decode("utf-8")
								track.put()

								cursor = query.cursor() 
							elif (extended_track["code"] == '403'):
								#Problem, to many queries, need to wait a bit to avoid quota limitation
								countdown = 10*60 # Wait 10 minutes before executing next element in queue
								break
							elif (extended_track["code"] == '404'):
								#Track removed from Youtube
								logging.info("Track removed from Youtube")
								track.youtube_duration = None
								track.youtube_title = None
								track.put()
								cursor = query.cursor()
							else:
								#Other problem, we skip the track
								cursor = query.cursor()

						except Exception, e:
							#If a problem occured, we skip the track
							logging.error("A problem occured...")
							logging.error(e)
							cursor = query.cursor()

					else:
						logging.info("Track up to date")
						cursor = query.cursor() 

				
				task = Task(
						url = "/taskqueue/upgrade",
						params = {'cursor':cursor, 'time':time},
						countdown = countdown,
					)
				task.add(queue_name = "upgrade-queue")
				logging.info("Task Upgrade put in the queue, with a delai of "+str(countdown/60)+" minutes")
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