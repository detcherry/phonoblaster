import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from controllers import facebook
from models.db.station import Station
from models.api.station import StationApi

class StationCreateHandler(BaseHandler):
	@login_required
	def get(self):
		template_values = {}
		
		user_contributions = self.user_proxy.contributions
		
		if(len(user_contributions) > 0):
			logging.info("User is admin of at least one page")
			user_page_ids = [contribution["page_id"] for contribution in user_contributions]
			results = Station.get_by_key_name(user_page_ids)
						
			contributions_left = []
			for i in range(len(results)):
				result = results[i]
				if result is None:
					contributions_left.append(user_contributions[i])
		else:
			self.user_proxy.reset_contributions()
			contributions_left = None
				
		template_values = {
			"user_contributions": contributions_left,
		}

		self.render("station/create.html", template_values)
	
	@login_required
	def post(self):
		if(self.user_proxy):
			page_id = self.request.get("page-id")
			page_shortname = self.request.get("page-shortname")[:30].lower()
			logging.info(page_id)
			logging.info(page_shortname)
			
			# We have to check if shortname is ok
			forbidden_characters = re.search("[^a-zA-Z0-9_]", page_shortname)
			existing_station = Station.all().filter("shortname", page_shortname).get()
			
			if(forbidden_characters or existing_station):
				self.error(403)
			else:
				# We check if the user is a page admin
				user_admin = self.user_proxy.is_admin_of(page_id)			
				if(user_admin):
					# We fetch some information about the facebook page (just the link in fact...)
					graph = facebook.GraphAPI()
					page_information = graph.get_object(page_id)
					
					logging.info(page_information)
					
					station_proxy = StationApi(page_shortname)
					station_proxy.put_station(page_id, page_shortname, page_information["name"], page_information["link"])
					
					self.redirect("/"+page_shortname)
				
				else:
					self.error(403)
		else:
			self.error(403)
		
		