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

		if key_name is not None:
			# Unique profile
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
			# Multiple profiles
			profiles = self.user_proxy.non_created_profiles
			if len(profiles) > 1:
				template_values = {
						"proceed": True,
						"unique": False,
						"profiles": profiles
					}
			elif len(profiles) == 1:
				template_values = {
						"proceed": True,
						"unique": True,
						"profile": profiles[0]
					}
			else:
				template_values = {
						"proceed": False
					}

		self.render("station/create.html", template_values)
	
	@login_required
	def post(self):
		key_name = self.request.get("key_name")
		shortname = self.request.get("shortname")[:30].lower()
		tracks = json.loads(self.request.get("tracks"))
		logging.info(key_name)
		
		# We have to check if shortname is ok
		forbidden_characters = re.search("[^a-zA-Z0-9_]", shortname)
		existing_station = Station.all().filter("shortname", shortname).get()
		
		if(forbidden_characters or existing_station):
			self.error(403)
		else:
			# We check if the user is a page admin
			user_admin = self.user_proxy.is_admin_of(key_name)
			if(user_admin):
				# We fetch some information about the facebook page (just the link in fact...)
				graph = facebook.GraphAPI(self.user_proxy.access_token)
				page_information = graph.get_object(key_name)
				
				station_proxy = StationApi(shortname)
				station_proxy.put_station(key_name, shortname, page_information["name"], page_information["link"], "page")
				user_proxy.set_profile(key_name)

				# Putting tracks in buffer
				for i in xrange(0,len(tracks)):
					track = tracks[i]
					track["type"] = "track"
					station_proxy.add_track_to_buffer(track)
			
				self.redirect("/"+shortname)
			elif key_name == self.user_proxy.user.key().name():
				# Station associated with User
				station_proxy = StationApi(shortname)
				station_proxy.put_station(key_name, shortname, self.user_proxy.user.first_name + ' ' + self.user_proxy.user.last_name, None, "user")
				user_proxy.set_profile(key_name)

				# Putting tracks in buffer
				for i in xrange(0,len(tracks)):
					track = tracks[i]
					track["type"] = "track"
					station_proxy.add_track_to_buffer(track)

				self.redirect("/"+shortname)

			else:
				self.error(403)

class ProfileSwitchHandler(BaseHandler):
	@login_required
	def get(self, key_name):
		# First we need to check if the key_name is in the non_created_profiles
		is_non_created = False
		for i in xrange(0,len(self.user_proxy.non_created_profiles)):
			if key_name == self.user_proxy.non_created_profiles[i]["key_name"]:
				is_non_created = True
				break

		if is_non_created:
			# The key_name was found in non created profile of current user, redirecting to /profile/init
			self.redirect("/profile/init?"+urllib.urlencode({ "key_name": key_name}))

		# Now we need to check if the key_name is in the created_profiles
		is_created = False
		for i in xrange(0,len(self.user_proxy.profiles)):
			if key_name == self.user_proxy.profiles[i]["key_name"]:
				is_created = True
				break

		if is_created:
			user_proxy.set_profile(key_name)
			shortname = user_proxy.profile["shortname"]
			self.redirect("/"+shortname)

		# If not created or created, it means key_name does not appear in user profiles -> unothorised
		self.error(404)

