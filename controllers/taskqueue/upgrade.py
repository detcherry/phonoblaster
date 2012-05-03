import logging
import traceback
import sys

from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api.taskqueue import Task

from models.api.user import UserApi

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
				user_key = comment.user.key()
				station_key = comment.station.key()
				user_proxy = UserApi(user_key.name())
				user_proxy.add_contribution(station_key)
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