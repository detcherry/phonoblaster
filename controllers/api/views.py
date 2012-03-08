import logging

from controllers.base import BaseHandler

from google.appengine.ext import db

from models.api.station import StationApi

from models.db.track import Track
from models.db.view import View

class ApiViewsHandler(BaseHandler):
	def post(self):
		logging.info("Deprecated")