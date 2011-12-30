import logging
from django.utils import simplejson as json

from controllers.base import BaseHandler
from models.api.station import StationApi

class GetCommentsHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		comments = station_proxy.comments
		self.response.out.write(json.dumps(comments))