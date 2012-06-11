import logging
import re
import urllib
import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler
from controllers.base import login_required

from controllers import facebook
from models.db.station import Station
from models.api.station import StationApi

class ProfileInitHandler(BaseHandler):
	@login_required
	def get(self):
		template_values = {}
		key_name = self.request.get("key_name")

		# Unique profile
		if key_name is not "":
			
			# Checking if key_name in user non created profiles
			is_non_created = False
			for i in xrange(0,len(self.user_proxy.non_created_profiles)):
				if key_name == self.user_proxy.non_created_profiles[i]["key_name"]:
					is_non_created = True
					profile = {
						"key_name": key_name,
						"name": self.user_proxy.non_created_profiles[i]["name"],
						"type": self.user_proxy.non_created_profiles[i]["type"]
					}
					break

			if is_non_created:
				# The key_name was found in non created profile of current user
				template_values = {
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
			# Multiple profiles
			profiles = self.user_proxy.non_created_profiles
			if len(profiles) > 1:
				template_values = {
					"unique": False,
					"profiles": profiles
				}
			elif len(profiles) == 1:
				template_values = {
					"unique": True,
					"profile": profiles[0]
				}
			else:
				self.redirect("/")

		self.render("profile.html", template_values)
	
	@login_required
	def post(self):
		key_name = self.request.get("key_name")
		shortname = self.request.get("shortname")[:30].lower()
		
		# We have to check if shortname is ok
		forbidden_characters = re.search("[^a-zA-Z0-9_]", shortname)
		existing_station = Station.all().filter("shortname", shortname).get()
		
		if(forbidden_characters or existing_station):
			logging.info("Forbidden characters or Existing station")
			self.error(403)
		else:
			if(key_name == self.user_proxy.user.key().name()):
				# Station associated with User
				station_proxy = StationApi(shortname)
				station_proxy.put_station(key_name, shortname, self.user_proxy.user.first_name + ' ' + self.user_proxy.user.last_name, None, "user")
				self.user_proxy.set_profile(key_name)

				self.response.out.write(json.dumps({'response': True}))
			elif(self.user_proxy.is_admin_of(key_name)):
				# We fetch some information about the facebook page (just the link in fact...)
				graph = facebook.GraphAPI(self.user_proxy.access_token)
				page_information = graph.get_object(key_name)
				
				station_proxy = StationApi(shortname)
				station_proxy.put_station(key_name, shortname, page_information["name"], page_information["link"], "page")
				self.user_proxy.set_profile(key_name)
			
				self.response.out.write(json.dumps({'response': True}))
			else:
				logging.info("User not admin")
				self.error(403)

class ProfileSwitchHandler(BaseHandler):
	@login_required
	def get(self, key_name):
		# First we need to check if the key_name is in the non_created_profiles
		logging.info(key_name)
		
		redirection = None
		template_values = None

		if self.user_proxy:
			is_non_created = False
			
			for i in xrange(0,len(self.user_proxy.non_created_profiles)):
				logging.info(self.user_proxy.non_created_profiles[i]["key_name"])
				
				if key_name == self.user_proxy.non_created_profiles[i]["key_name"]:
					is_non_created = True
					profile = {
						"key_name": key_name,
						"name": self.user_proxy.non_created_profiles[i]["name"],
						"type": self.user_proxy.non_created_profiles[i]["type"]
					}
					logging.info(profile)
					break

			if is_non_created:
				logging.info("Is Non Created!")
				# The key_name was found in non created profile of current user, redirecting to /profile/init
				template_values = {
					"unique": True,
					"profile": profile
				}
				self.render("profile.html", template_values)

			# Now we need to check if the key_name is in the created_profiles
			is_created = False
			for i in xrange(0,len(self.user_proxy.profiles)):
				if key_name == self.user_proxy.profiles[i]["key_name"]:
					shortname = self.user_proxy.profiles[i]["shortname"]
					redirection = "/" + shortname
					is_created = True
					break

			if is_created:
				logging.info("Is Created!")
				self.user_proxy.set_profile(key_name)

		if is_non_created:
			self.render("profile.html", template_values)
		else:
			if redirection:
				self.redirect(redirection)
			else:
				self.error(404)


		"""
		self.redirect("/")

		# If not created or created, it means key_name does not appear in user profiles -> unothorised
		self.error(404)
		"""
