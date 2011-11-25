from base import BaseHandler

class HomeHandler(BaseHandler):
	def get(self):
		template_values = {}
		if(self.current_user):
			template_values = { "id": self.current_user.twitter_id }
		self.render("base.html", template_values)