import logging

from django.utils import simplejson as json

from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi


class ApiTapesHandeler(BaseHandler):
	"""
		
	"""

	@login_required
	def get(self):
		shortname = self.request.get("shortname")
		logging.info("Station shortname : "+shortname)
		station_proxy = StationApi(shortname)
		station = station_proxy.station

		if(station):
			if(self.user_proxy.is_admin_of(station.key().name())):
				logging.info("Station retrieved")
				tapes = station_proxy.tapes
				logging.info("Tapes retrieved")
				json_tapes = {"tapes":tapes}
				self.response.out.write(json.dumps(str(json_tapes))) #TESTING, TO BE REMOVED
			else:
				logging.info("User not allowed")
				self.redirect("/"+shortname)
		else:
			self.error(404)

	@login_required
	def post(self):
		self.response.out.write("TO BE DONE")
		
		