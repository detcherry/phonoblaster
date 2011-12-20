import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.station import Station

class StationCreateHandler(BaseHandler):
	@login_required
	def post(self):
		if(self.user_proxy):
			page_id = self.request.get("page-id")
			page_shortname = self.request.get("page-shortname")[:30].lower()
			
			page_contribution = self.user_proxy.get_page_contribution(page_id)
			
			# User is an admin of this page
			if(page_contribution):
				# We have to strip fordbidden characters in case user has made shit
				page_shortname = re.sub("[^a-zA-Z0-9_]", "", page_shortname)
				
				# We put the station in the datastore
				station = Station(
					key_name = page_id,
					name = page_contribution["page_name"],
					shortname = page_shortname,
				)
				station.put()
				logging.info("New station %s put in the datastore" %(station.name))
								
				self.redirect("/"+station.shortname)
				
			else:
				self.error(403)
		else:
			self.error(403)
		
		