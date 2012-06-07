import logging
import re

from controllers.base import BaseHandler
from controllers.base import login_required

from controllers import facebook
from models.db.station import Station
from models.api.station import StationApi

class ProfileHandler(BaseHandler):
	@login_required
	def get(self):
		template_values = {}
		key_name = self.request.get("key_name")

		if key_name is not None:
			# Specific Process
			# Checking if key_name in user non created profiles
			is_non_created = False
			for i in xrange(0,len(self.user_proxy.non_created_profiles)):
				if key_name == self.user_proxy.non_created_profiles[i]["key_name"]:
					is_non_created = True
					profile = 
						{
							"key_name": key_name,
							"name": self.user_proxy.non_created_profiles[i]["name"],
							"type": self.user_proxy.non_created_profiles[i]["type"]
						}
					break

			if is_non_created:
				# The key_name was found in non created profile of current user
				template_values = 
					{
						"proceed": True,
						"unique": True,
						"profile": profile
					}
			else:
				is_created = False
				# The key_name was not found in non created profiles, is the key_name associated with an existing station?
				for i in xrange(0,len(self.user_proxy.profiles)):
					if key_name == self.user_proxy.profiles[i]["key_name"]:
						# key_name is actually the one of a created station
						is_created = True
						break
				
				if is_created:
					self.redirect('/'+self.user_proxy.profiles[i]["shortname"])
				else:
					# Throwing error
					self.error(404)

		else:
			# Global process
			profiles = self.user_proxy.non_created_profiles
			if len(profiles) > 1:
				template_values = 
					{
						"proceed": True,
						"unique": False,
						"profiles": profiles
					}
			elif len(profiles) == 1:
				template_values =
					{
						"proceed": True,
						"unique": True,
						"profile": profiles[0]
					}
			else:
				template_values =
					{
						"proceed": False
					}

		self.render("station/create.html", template_values)
	
	@login_required
	def post(self):
		page_id = self.request.get("page-id")
		page_shortname = self.request.get("page-shortname")[:30].lower()
		logging.info(page_id)
		
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
				graph = facebook.GraphAPI(self.user_proxy.access_token)
				page_information = graph.get_object(page_id)
				
				station_proxy = StationApi(page_shortname)
				station_proxy.put_station(page_id, page_shortname, page_information["name"], page_information["link"])
			
				self.redirect("/"+page_shortname)
			
			else:
				self.error(403)