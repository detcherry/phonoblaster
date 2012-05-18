import logging

from models.api.station import StationApi
from models.db.station import Station

from base import BaseHandler
from base import login_required

class BufferHandler(BaseHandler):
	@login_required
	def get(self, shortname):
		self.render("buffer_test.html",{'shortname':shortname})