import logging

from controllers.base import BaseHandler

from models.api.station import StationApi


class ApiTapesHandeler(BaseHandler):
	"""
		
	"""

	def get(self):
		shortname = self.request.get("shortname")
		logging.info("Station shortname : "+shortname)
		station_proxy = StationApi(shortname)
		station = station_proxy.station

		if(station):
			logging.info("Station retrieved")
			tapes = station_proxy.tapes
			logging.info("Tapes retrieved")
			self.response.out.write("Result : "+str(tapes[0]["key_name"])) #TESTING, TO BE REMOVED
		else:
			self.error(404)

	def post(self):
		self.response.out.write("TO BE DONE")
		pass
		