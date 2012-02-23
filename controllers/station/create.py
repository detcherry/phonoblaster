import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from controllers import facebook
from models.db.station import Station

class StationCreateHandler(BaseHandler):
	@login_required
	def get(self):
		template_values = {}
		
		user_contributions = self.user_proxy.contributions
		
		user_stations = None
		if user_contributions:
			logging.info("User is admin of at least one page")
			user_page_ids = [contribution["page_id"] for contribution in user_contributions]
			results = Station.get_by_key_name(user_page_ids)
			
			for i in range(len(results)):
				result = results[i]
				if result is not None:
					# Remove contribution from list (station already created)
					user_contributions.pop(i)
				
		template_values = {
			"user_contributions": user_contributions,
		}

		self.render("station/create.html", template_values)
	
	@login_required
	def post(self):
		if(self.user_proxy):
			page_id = self.request.get("page-id")
			page_shortname = self.request.get("page-shortname")[:30].lower()
			
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
					graph = facebook.GraphAPI(self.user_proxy.user.facebook_access_token)
					page_information = graph.get_object(page_id)
					
					station = Station(
						key_name = page_id,
						shortname = page_shortname,
						name = page_information["name"],
						link = page_information["link"],
					)
					station.put()
					
					logging.info("New station %s put in the datastore" %(station.name))
					self.redirect("/"+station.shortname)
				
				else:
					self.error(403)
		else:
			self.error(403)
		
		