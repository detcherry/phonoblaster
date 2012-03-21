import logging

from controllers.base import BaseHandler


class ApiTapesHandeler(BaseHandler):
	"""
		
	"""

	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station

		if(station):
			logging.info("Station retrieved")
			tapes = station_proxy.tapes()


		else:
			self.error(404)

	def post(self):
		self.out.write("TO BE DONE")
		pass
		