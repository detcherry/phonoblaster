import logging

from base import BaseHandler
from controllers import facebook
from models.db.station import Station

class HomeHandler(BaseHandler):
	def get(self):
		if(self.user_proxy):
			self.redirect("/station/create")
		else:
			self.render("welcome.html", None)