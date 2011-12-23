import logging
from controllers.base import BaseHandler

class RootHandler(BaseHandler):
	
	def render(self, template_path, template_values):
		if template_values:
			self._template_values = template_values
		else:
			self._template_values = {}
		
		self._template_values["station_proxy"] = self.station_proxy		
		super(RootHandler, self).render(template_path, self._template_values)