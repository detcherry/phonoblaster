import logging
from controllers.base import BaseHandler

from models.api.user import UserApi

class ProfileHandler(BaseHandler):
	def get(self, key_name):
		profile_proxy = UserApi(key_name)
		
		template_values = {
			"profile_proxy": profile_proxy,
			"number_of_favorites": profile_proxy.number_of_favorites,
		}
		
		self.render("profile.html", template_values)
		
		
		