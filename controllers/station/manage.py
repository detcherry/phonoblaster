import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from controllers import facebook
from models.db.station import Station
from models.api.station import StationApi

class StationManagelHandler(BaseHandler):
	@login_required
	def get(self):
		template_values = {}
		
		self.user_proxy.reset_contributions()
		user_contributions = self.user_proxy.contributions
		
		if(len(user_contributions) > 0):
			logging.info("User is admin of at least one page")
			user_page_ids = [contribution["page_id"] for contribution in user_contributions]
			results = Station.get_by_key_name(user_page_ids)
						
			contributions_installed = []
			for i in range(len(results)):
				result = results[i]
				if result is not None:
					contributions_installed.append(user_contributions[i])
		else:
			contributions_installed = None
				
		template_values = {
			"user_contributions": contributions_installed,
		}

		self.render("station/manage.html", template_values)