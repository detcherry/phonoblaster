import os.path
import logging

import controllers.config
import controllers.facebook 
from controllers.decorators import *

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from models.db.user import User
from models.interface.user import InterfaceUser

from google.appengine.ext.db import BadArgumentError

class BaseHandler(webapp.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """

    @property
    def current_user(self):
		if not hasattr(self, "_current_user"):
			self._current_user = None
			cookie = controllers.facebook.get_user_from_cookie(
				self.request.cookies,
				controllers.config.FACEBOOK_APP_ID,
				controllers.config.FACEBOOK_APP_SECRET
			)
			if cookie:
				# Store a local instance of the user data so we don't need
				# a round-trip to Facebook on every request
				user = InterfaceUser.get_by_facebook_id(cookie["uid"])
				if not user:
					graph = controllers.facebook.GraphAPI(cookie["access_token"])
					profile = graph.get_object("me")
					user = InterfaceUser.put(
						facebook_id = str(profile["id"]), 
						facebook_access_token = cookie["access_token"],
						name = profile["name"],
						first_name = profile["first_name"],
						last_name = profile["last_name"],
						email = profile["email"]
					)
					logging.info("New user %s" %(user.name))
				else:
					if not user.email or user.facebook_access_token != cookie["access_token"]:
						email = None
						facebook_access_token = None
						
						if not user.email:
							graph = controllers.facebook.GraphAPI(cookie["access_token"])
							profile = graph.get_object("me")
							email = profile["email"]
						
						if user.facebook_access_token != cookie["access_token"]:
							facebook_access_token = cookie["access_token"]
						
						user = InterfaceUser.put_email_and_access_token(user, email, facebook_access_token)
					
				self._current_user = user
		return self._current_user
	
    @property
    def template_values(self):
		if not hasattr(self,"_template_values"):
			self._template_values = {
				"current_user": self.current_user,
				"facebook_app_id": controllers.config.FACEBOOK_APP_ID,
				"google_analytics_id": controllers.config.GOOGLE_ANALYTICS_ID,
			}
			for key, value in self.additional_template_values.iteritems():
				self._template_values[key] = value
		return self._template_values

    def render(self, template_path):
	    path = os.path.join(os.path.dirname(__file__), template_path)
	    self.response.out.write(template.render(path, self.template_values))

    def handle_exception(self, exception, debug_mode):
	    logging.info(exception)
	    path = os.path.join(os.path.dirname(__file__), "../templates/error.html")
	    self.response.out.write(template.render(path, None))
		
		