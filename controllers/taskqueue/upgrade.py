import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

from models.db.user import User
from models.db.station import Station
from models.db.comment import Comment

class UpgradeHandler(webapp.RequestHandler):
	def post(self):
		cursor = self.request.get("cursor")

		query = User.all()
		if(cursor):
			logging.info("Cursor found")
			query.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")

		users = query.fetch(100)

		if(users):
			logging.info("Users found")
			for user in users:
				if(user.stations):
					logging.info("Stations found for %s %s"%(user.first_name, user.last_name))
				else:
					logging.info("Stations not found for %s %s"%(user.first_name, user.last_name))
					user.stations = []
					user.put()

			cursor = query.cursor()
			task = Task(
					url = "/taskqueue/upgrade",
					params = {'cursor':cursor},
					countdown = 1 ,
				)
			task.add(queue_name = "upgrade-queue")
		else:
			logging.info("No More users, terminating update")





application = webapp.WSGIApplication([
	(r"/taskqueue/upgrade", UpgradeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	