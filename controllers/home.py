from base import BaseHandler

class HomeHandler(BaseHandler):
	def get(self):
		template_values = {}
		if(self.current_user):
			self.redirect("/"+self.current_user.username)
		self.render("home.html", template_values)
		