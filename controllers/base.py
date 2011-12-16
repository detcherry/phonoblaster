import os.path
import logging
import traceback
import sys
from django.utils import simplejson

from config import *

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from functools import wraps
def login_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.current_user
        if not user:
            if self.request.method == "GET":
				redirection = {
					"client_id": FACEBOOK_APP_ID,
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
	def current_user(self):
		if not hasattr(self, "_current_user"):
			self._current_user = None
		return self._current_user

	# Custom rendering function
	def render(self, template_path, template_values):
		if template_values:
			self.template_values = template_values
		else:
			self.template_values = {}
		
		# Standard template values
		self.template_values["current_user"] = self.current_user
		self.template_values["google_analytics_id"] = GOOGLE_ANALYTICS_ID
		self.template_values["facebook_app_id"] = FACEBOOK_APP_ID
		self.template_values["site_url"] = SITE_URL
		
		relative_path = os.path.join("../templates/", template_path)
		path = os.path.join(os.path.dirname(__file__), relative_path)
		self.response.out.write(template.render(path, self.template_values))

	# Handle exceptions, errors that are raised
	def handle_exception(self, exception, debug_mode):
		logging.error(''.join(traceback.format_exception(*sys.exc_info())))
		if self.request.method == "GET":
			path = os.path.join(os.path.dirname(__file__), "../templates/error.html")
			self.response.out.write(template.render(path, None))
		else:
			self.response.out.write(simplejson.dumps({"error":"An error occurred."}))
