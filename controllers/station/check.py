import logging
import json

from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.station import Station

class StationCheckHandler(BaseHandler):
	def post(self):
		shortname = self.request.get("shortname")[:30].lower()
		
		availability = False
		existing_station = Station.all().filter("shortname", shortname).get()
		if not existing_station:
			availability = True
			
		self.response.out.write(json.dumps({"availability": availability}))
