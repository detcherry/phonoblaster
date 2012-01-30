from datetime import datetime

import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.station import StationApi

class ApiRecommandationsHandler(BaseHandler):
	@login_required
	def get(self):
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		offset = datetime.utcfromtimestamp(int(self.request.get("offset")))
		
		extended_tracks = station_proxy.get_recommandations(offset)
		
		self.response.out.write(json.dumps(extended_tracks))