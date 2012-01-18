import logging
from datetime import datetime
from django.utils import simplejson as json

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.track import Track

class ApiLibraryHandler(BaseHandler):
	@login_required
	def get(self):
		offset = datetime.utcfromtimestamp(int(self.request.get("offset")))
		extended_tracks = self.user_proxy.get_library(offset)
		self.response.out.write(json.dumps(extended_tracks))