import os.path
import logging
import traceback
import re
import sys

from controllers import config
from controllers import facebook

import webapp2
import jinja2
import json

from models.api.user import UserApi

from functools import wraps
def login_required(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		user_proxy = self.user_proxy
		if not user_proxy:
			if self.request.method == "GET":
				self.redirect("/")
				return
			self.error(403)
		else:
			profile = user_proxy.profile
			
			if re.match('/profile/switch/([0-9]+)',self.request.path) or self.request.path == '/profile/init' or profile:
				return method(self, *args, **kwargs)
			else:
				if self.request.method == "GET":
					self.redirect('/profile/init')
					return
				self.error(403)
	return wrapper

def profile_required(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		user_proxy = self.user_proxy
		if not user_proxy:
			return method(self, *args, **kwargs)
		else:
			profile = user_proxy.profile
			
			if re.match('/profile/switch/([0-9]+)',self.request.path) or self.request.path == '/profile/init' or profile:
				return method(self, *args, **kwargs)
			else:
				if self.request.method == "GET":
					self.redirect('/profile/init')
					return
				self.error(403)
	return wrapper

def admin_required(method):
	@wraps(method)
	def wrapper(self, *args, **kwargs):
		admin = False

		if self.user_proxy:
			uid = self.user_proxy.user.key().name()
			if uid in ["663812262","698198735"]:
				admin = True

		if not admin:
			if self.request.method == "GET":
				self.redirect("/")
				return
			self.error(403)
		else:
			return method(self, *args, **kwargs)
	return wrapper

class BaseHandler(webapp2.RequestHandler):
	
	@property
	def user_proxy(self):
		if not hasattr(self, "_user_proxy"):
			self._user_proxy = None
			cookie = self.request.cookies.get("fbsr_" + config.FACEBOOK_APP_ID, "")
			
			# Cookie obviously set by Facebook
			if cookie:
				response = facebook.parse_signed_request(cookie, config.FACEBOOK_APP_SECRET)
				
				# Cookie certainly set by Facebook
				if response:
					user_proxy = UserApi(response["user_id"], response["code"])
					user = user_proxy.user

					# If not registered, save the new user
					if not user:
						graph = facebook.GraphAPI(user_proxy.access_token)
						profile = graph.get_object("me")
						if "email" in profile:		
							user = user_proxy.put_user(
								response["user_id"], 
								profile["first_name"],
								profile["last_name"],
								profile["email"]
							)
							logging.info("New user: %s %s" %(user.first_name, user.last_name))

					self._user_proxy = user_proxy

		return self._user_proxy
	
	# Custom rendering function
	def render(self, template_path, template_values):
		self._template_values = {}
		if template_values:
			self._template_values = template_values
		
		# Standard template values
		self._template_values["user_proxy"] = self.user_proxy
		self._template_values["domain"] = config.DOMAIN
		self._template_values["google_analytics_id"] = config.GOOGLE_ANALYTICS_ID
		self._template_values["facebook_app_id"] = config.FACEBOOK_APP_ID
		self._template_values["soundcloud_app_id"] = config.SOUNDCLOUD_APP_ID
		self._template_values["site_url"] = config.SITE_URL
		self._template_values["version"] = config.VERSION
		self._template_values["tag"] = config.TAG

		# Information below necessary for header
		if self.user_proxy and self.user_proxy.profile:
			
			# Only user profile owned by user or more than that?
			self._template_values["one_profile"] = True
			if len(self.user_proxy.profiles) > 1:
				self._template_values["one_profile"] = False

			# Retrieving all profiles associated with user except the current profile
			user_profiles = self.user_proxy.profiles
			self._template_values["non_default_profiles"] = []
			for p in user_profiles:
				if self.user_proxy.profile["key_name"] != p["key_name"]:
					self._template_values["non_default_profiles"].append(p)
		
		templates = os.path.join(os.path.dirname(__file__),"../templates/")
		jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
		template = jinja.get_template(template_path)
		self.response.out.write(template.render(self._template_values))

	# Handle exceptions, errors that are raised
	def handle_exception(self, exception, debug_mode):
		logging.error(''.join(traceback.format_exception(*sys.exc_info())))
		if self.request.method == "GET":
			template_values = {
				"domain": config.DOMAIN,
				"google_analytics_id": config.GOOGLE_ANALYTICS_ID,
				"facebook_app_id": config.FACEBOOK_APP_ID,
				"site_url": config.SITE_URL,
				"version": config.VERSION,
				"tag": config.TAG,
			}
			
			templates = os.path.join(os.path.dirname(__file__),"../templates/")
			jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
			template = jinja.get_template("error.html")
			self.response.out.write(template.render(template_values))
			
		else:
			self.response.out.write(json.dumps({"error":"An error occurred."}))
