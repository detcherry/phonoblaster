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
		youtubeErrorRaied = False

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
			tracks = query.fetch(1)
			if (tracks):
				for track in tracks:
					logging.info("Track Youtube id : "+track.youtube_id)
					if((not track.youtube_duration) or (not track.youtube_title)):
						logging.info("Youtube API Call is necessary")
						try:
							extended_track = Youtube.get_extended_tracks([track.youtube_id])[0]
							youtube_duration = int(extended_track["duration"])
							youtube_title = extended_track["title"]


							track.youtube_duration = youtube_duration
							track.youtube_title = youtube_title.decode("utf-8")
							track.put()
						except Exception, e:
							logging.info("Task Upgrade put in the queue, with a delai of 10 minutes")
							youtubeErrorRaied = True
							break

					else:
						logging.info("Track up to date")

				if(youtubeErrorRaied):
					countdown = 10*60 # Wait 10 minutes before executing next element in queue
				else:
					countdown = 0
				
				cursor = query.cursor()
				task = Task(
						url = "/taskqueue/upgrade",
						params = {'cursor':cursor, 'time':time},
						countdown = countdown,
					)
				task.add(queue_name = "upgrade-queue")
				logging.info("Task Upgrade put in the queue")


application = webapp.WSGIApplication([
	(r"/taskqueue/upgrade", DBUpgradeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	