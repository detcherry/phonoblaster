import logging

from controllers.base import BaseHandler

class RootHandler(BaseHandler):
	
	@property
	def number_of_broadcasts(self):
		return None
		
	@property
	def number_of_influencer_of(self):
		return None
		
	@property
	def number_of_influenced_by(self):
		return None
			
	def root_render(self, template_path, template_values):
		if template_values:
			root_template_values = template_values
		else:
			root_template_values = {}
		
		root_template_values["current_broadcaster"] = self.current_broadcaster
		root_template_values["number_of_broadcasts"] = self.number_of_broadcasts
		root_template_values["number_of_influencer_of"] = self.number_of_influencer_of
		root_template_values["number_of_influenced_by"] = self.number_of_influenced_by
		
		self.render(template_path, root_template_values)
		
		