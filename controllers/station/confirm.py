import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.station import Station

class StationConfirmHandler(BaseHandler):
	@login_required
	def post(self):
		page_id = self.request.get("page-id")
		page_shortname = self.request.get("page-shortname").lower()
		
		shortname_correct = False
		# We strip every forbidden characters
		page_shortname = re.sub("[^a-zA-Z0-9_]", "", page_shortname)
		if len(page_shortname) <= 30:
			shortname_correct = True
		
		if shortname_correct:
			existing_station = Station.all().filter("shortname", page_shortname).get()
			if not existing_station:
				station = Station.get_by_key_name(page_id)
				station.shortname = page_shortname
				station.put()
				logging.info("Station updated with a shortname")
				self.redirect("/"+station.shortname)
		
			else:
				logging.info("Station shortname not available")
				self.error(403)
		else:
			logging.info("Station shortname not correct")
			self.error(403)
		