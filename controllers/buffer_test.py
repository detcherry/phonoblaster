import logging

from models.api.station import StationApi

from base import BaseHandler
from base import login_required

class BufferHandler(BaseHandler):
	@login_required
	def get(self, shortname):
		station_proxy = StationApi(shortname)

		if(station_proxy):
			buffer = station_proxy.buffer_and_timestamp
			duration = station_proxy.get_buffer_duration()

		template_values = {'shortname': shortname, 'buffer':buffer['buffer'], 'timestamp': buffer['timestamp'], 'duration':duration }
		self.render("buffer_test.html",template_values)