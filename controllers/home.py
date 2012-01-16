import logging

from base import BaseHandler
from controllers import facebook
from models.db.station import Station

class HomeHandler(BaseHandler):
	def get(self):
		template_values = {}
		
		if(self.user_proxy):
			user_contributions = self.user_proxy.contributions
			
			user_stations = None
			if user_contributions:
				logging.info("User is admin of at least one page")
				user_page_ids = []
				for contribution in user_contributions:
					user_page_ids.append(contribution["page_id"])
				
				# Check if some pages have been already created
				user_stations = []
				results = Station.get_by_key_name(user_page_ids)
				for result in results:
					if result is not None:
						logging.info("User is admin of at least one station")
						user_stations.append(result)
			
			template_values = {
				"user_stations": user_stations,
				"user_contributions": user_contributions,
			}
			
		self.render("home.html", template_values)
		