import logging

from controllers.base import profile_required
from controllers.station.root import RootHandler
from models.api.station import StationApi

from google.appengine.ext import blobstore

class StationHandler(RootHandler):
	@profile_required
	def get(self, shortname):
		self.station_proxy = StationApi(shortname)
	
		if(self.station_proxy.station):
			url = "/api/" + shortname + "/background"
			template_values = {
				"blobstore_url": blobstore.create_upload_url(url),
			}

			self.render("station/station.html", template_values)
		else:
			self.render("station/404.html", None)