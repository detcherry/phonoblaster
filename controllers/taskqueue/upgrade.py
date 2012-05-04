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

		query = Comment.all().filter("admin = ", True)
		if(cursor):
			logging.info("Cursor found")
			query.with_cursor(start_cursor = cursor)
		else:
			logging.info("No cursor")

		comments = query.fetch(100)

		if(comments):
			logging.info("Comments found")
			for comment in comments:
				user = comment.user
				station_key = comment.station.key()
				if(user.stations):
					logging.info("%s %s already has a station list"%(user.first_name, user.last_name))
				else:
					user.stations = []
					logging.info("Initialization : %s %s has a no station list"%(user.first_name, user.last_name))

				if(station_key not in user.stations):
					user.stations.append(station_key)
					user.put()
					logging.info("Adding %s to list station of %s %s"%(comment.station.shortname, user.first_name, user.last_name))
				else:
					logging.info("%s %s already admin of %s"%(user.first_name, user.last_name, comment.station.shortname))
			cursor = query.cursor()
		else:
			logging.info("No More comments, terminating update")





application = webapp.WSGIApplication([
	(r"/taskqueue/upgrade", UpgradeHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	