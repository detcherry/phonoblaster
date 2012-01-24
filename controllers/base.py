import os.path
import logging
import traceback
import sys
import urllib

from controllers import config
from controllers import facebook

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.utils import simplejson as json

from models.api.user import UserApi

from functools import wraps
def login_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        user_proxy = self.user_proxy
        if not user_proxy:
            if self.request.method == "GET":
				redirection = {
					"client_id": config.FACEBOOK_APP_ID,
					"redirect_uri": self.request.url,
					"scope": "email,publish_actions,read_stream,publish_stream,manage_pages"
				}
				self.redirect("https://www.facebook.com/dialog/oauth?" + urllib.urlencode(redirection))
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
			cookie = facebook.get_user_from_cookie(
				self.request.cookies,
				config.FACEBOOK_APP_ID,
				config.FACEBOOK_APP_SECRET
			)
			if cookie:
				# Store a local instance of the user data so we don't need a round-trip to Facebook on every request
				user_proxy = UserApi(cookie["uid"])
				user = user_proxy.user
				
				# If not registered, save the new user
				if not user:
					graph = facebook.GraphAPI(cookie["access_token"])
					profile = graph.get_object("me")
					user = user_proxy.put_user(
						cookie["uid"], 
						cookie["access_token"],
						profile["first_name"],
						profile["last_name"],
						profile["email"]
					)
					logging.info("New user: %s %s" %(user.first_name, user.last_name))
				else:
					# If token is different, update the token
					if user.facebook_access_token != cookie["access_token"]:
						user_proxy.update_token(cookie["access_token"])
						logging.info("Token updated in user %s %s"%(user.first_name, user.last_name))
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
		self._template_values["google_analytics_id"] = config.GOOGLE_ANALYTICS_ID
		self._template_values["facebook_app_id"] = config.FACEBOOK_APP_ID
		self._template_values["site_url"] = config.SITE_URL
		self._template_values["version"] = config.VERSION
		
		relative_path = os.path.join("../templates/", template_path)
		path = os.path.join(os.path.dirname(__file__), relative_path)
		self.response.out.write(template.render(path, self._template_values))

	# Handle exceptions, errors that are raised
	def handle_exception(self, exception, debug_mode):
		logging.error(''.join(traceback.format_exception(*sys.exc_info())))
		if self.request.method == "GET":
			path = os.path.join(os.path.dirname(__file__), "../templates/error.html")
			self.response.out.write(template.render(path, None))
		else:
			self.response.out.write(json.dumps({"error":"An error occurred."}))
