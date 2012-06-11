import os.path
import logging
import traceback
import sys
import urllib

from controllers import config
from controllers import facebook

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import django_setup
from django.utils import simplejson as json

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
			
			if profile or self.request.path == '/profile/switch' or self.request.path == '/profile/init':
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
			
			if profile or self.request.path == '/profile/switch' or self.request.path == '/profile/init':
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
			if uid in ["663812262","698198735","1478671803"]:
				admin = True

		if not admin:
			if self.request.method == "GET":
				self.redirect("/")
				return
			self.error(403)
		else:
			return method(self, *args, **kwargs)
	return wrapper

class BaseHandler(webapp.RequestHandler):
	@property
	def user_proxy(self):
		if not hasattr(self, "_user_proxy"):
			self._user_proxy = None
			cookie = self.request.cookies.get("fbsr_" + config.FACEBOOK_APP_ID, "")
			if cookie:
				response = facebook.parse_signed_request(cookie, config.FACEBOOK_APP_SECRET)
				if response:
					user_proxy = UserApi(response["user_id"], code=response["code"])
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
						else:
							logging.error("User does not share his email. Strange...")
					
					#self._user_proxy = user_proxy
					
					# patch below before login has gone full client
					access_token = user_proxy.access_token
					if user and access_token:
						self._user_proxy = user_proxy
		
		return self._user_proxy

	# Custom rendering function
	def render(self, template_path, template_values):
		if template_values:
			self._template_values = template_values
		else:
			self._template_values = {}
		
		# Standard template values
		self._template_values["user_proxy"] = self.user_proxy
		self._template_values["domain"] = config.DOMAIN
		self._template_values["google_analytics_id"] = config.GOOGLE_ANALYTICS_ID
		self._template_values["facebook_app_id"] = config.FACEBOOK_APP_ID
		self._template_values["site_url"] = config.SITE_URL
		self._template_values["version"] = config.VERSION
		self._template_values["tag"] = config.TAG

		# Profiles information
		if len(self.user_proxy.contributions) > 0:
			self._template_values["unique"] = True
		else:
			self._template_values["unique"] = False

		# Adding all profiles associated with users
		user_profiles = self.user_proxy.profiles + self.user_proxy.non_created_profiles
		self._template_values["profiles"] = []
		for p in user_profiles:
			self._template_values["profiles"].append({
				"key_name": p["key_name"],
				"name": p["name"],
				})

		
		relative_path = os.path.join("../templates/", template_path)
		path = os.path.join(os.path.dirname(__file__), relative_path)
		self.response.out.write(template.render(path, self._template_values))

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
			path = os.path.join(os.path.dirname(__file__), "../templates/error.html")
			self.response.out.write(template.render(path, template_values))
		else:
			self.response.out.write(json.dumps({"error":"An error occurred."}))
