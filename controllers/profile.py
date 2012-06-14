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
		template_values = None
		redirection = None
		key_name = self.request.get("key_name")
		user_profiles = self.user_proxy.profiles

		# Unique profile
		if key_name is not "":
			profile = None
			
			# Checking if key_name is in non created profiles or is associated to a created profile
			for i in xrange(0,len(user_profiles)):
				if key_name == user_profiles[i]["key_name"]:
					if user_profiles[i]["created"] is None: 
						template_values = {
							"unique": True,
							"profile": user_profiles[i]
						}
						break
					else:
						redirection = "/"+user_profiles[i]["shortname"]
		else:			
			# Multiple profiles
			if len(user_profiles) >1:
				template_values = {
					"unique": False,
					"profiles": user_profiles
				}
			elif len(user_profiles) == 1 and (user_profiles[0]["created"] is None):
				template_values = {
					"unique": True,
					"profile": user_profiles[0]
				}
			else:
				redirection = "/"+self.user_proxy.profile["shortname"]

		# Deciding what to return
		if redirection is not None:
			self.redirect(redirection)
		elif template_values is not None:
			self.render("profile.html", template_values)
		else:
			# Throwing error
			self.error(404)
		
	
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
			if key_name == self.user_proxy.user.key().name():
				# Station associated with User, we have to know first if associated station was created
				user_profiles = self.user_proxy.profiles
				for i in xrange(0,len(user_profiles)):
					if key_name == user_profiles[i]["key_name"] and user_profiles[i]["created"] is None:
						station_proxy = StationApi(shortname)
						station_proxy.put_station(key_name, shortname, self.user_proxy.user.first_name + ' ' + self.user_proxy.user.last_name, None, "user")
						self.user_proxy.set_profile(key_name)
						self.response.out.write(json.dumps({'response': True}))
						break
			elif self.user_proxy.is_admin_of(key_name):
				# We fetch some information about the facebook page
				graph = facebook.GraphAPI(self.user_proxy.access_token)
				page_information = graph.get_object(key_name)
				user_profiles = self.user_proxy.profiles

				for i in xrange(0,len(user_profiles)):
					if key_name == user_profiles[i]["key_name"] and user_profiles[i]["created"] is None:
						station_proxy = StationApi(shortname)
						station_proxy.put_station(key_name, shortname, page_information["name"], page_information["link"], "page")
						self.user_proxy.set_profile(key_name)
						self.response.out.write(json.dumps({'response': True}))
						break
			else:
				logging.info("User not admin")
				self.error(403)

class ProfileSwitchHandler(BaseHandler):
	@login_required
	def get(self, key_name):
		# First we need to check if the key_name is in the non_created_profiles
		logging.info(key_name)

		user_profiles = self.user_proxy.profiles	
		redirection = None
		template_values = None

		if self.user_proxy:
			is_non_created = False
			
			for i in xrange(0,len(user_profiles)):
				if key_name == user_profiles[i]["key_name"] and user_profiles[i]["created"] is None:
					profile = user_profiles[i]
					template_values = {
						"unique": True,
						"profile": profile
					}
					break
				elif key_name == user_profiles[i]["key_name"] and user_profiles[i]["created"] is not None:
					shortname = self.user_proxy.profiles[i]["shortname"]
					redirection = "/" + shortname
					self.user_proxy.set_profile(key_name)
					break

		if template_values:
			self.render("profile.html", template_values)
		elif redirection:
			self.redirect(redirection)
		else:
			self.error(404)
