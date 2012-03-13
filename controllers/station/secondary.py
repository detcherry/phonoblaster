import logging

from controllers.station.root import RootHandler
from datetime import datetime

class SecondaryHandler(RootHandler):
	def render(self, template_path, template_values):
		if template_values:
			self._template_values = template_values
		else:
			self._template_values = {}
			
		try:
			self._template_values["latest_broadcasts"] = self.station_proxy.get_broadcasts(datetime.utcnow())
		except:
			# in case of a 404 error
			logging.info("No station proxy")
		
		super(SecondaryHandler, self).render(template_path, self._template_values)
	
	# Render templates for Facebook linter
	def facebook_render(self, template_path, template_values):
		super(SecondaryHandler, self).render(template_path, template_values)