import os
import logging
import traceback
import sys
import urllib

from config import *
from library.gaesessions import get_current_session

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from models.db.user import User
from models.api.user import UserApi

from functools import wraps
def login_required(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        user = self.current_user
        if not user:
            if self.request.method == "GET":
				redirection = {"redirect_url": self.request.url}
				self.redirect("/account/login?" + urllib.urlencode(redirection))
				return
            self.error(403)
        else:
            return method(self, *args, **kwargs)
    return wrapper


class BaseHandler(webapp.RequestHandler):
    """
		Provides access to the active Twitter user in self.current_user
    """
    @property
    def current_user(self):
		if not hasattr(self, "_current_user"):
			self._current_user = None
			session = get_current_session()
			username = session.get("username")
			
			# If username is set in the session, that means user has signed in
			if username:
				user_proxy = UserApi(username)
				self._current_user = user_proxy.user
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
	    path = os.path.join(os.path.dirname(__file__), "../templates/error.html")
	    self.response.out.write(template.render(path, None))

