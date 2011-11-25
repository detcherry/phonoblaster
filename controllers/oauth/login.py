from controllers.base import BaseHandler

# Screen for user to log in
class TwitterLoginHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.render("oauth/login.html", None)
		else:
			# If user logged in, redirect to homepage
			self.redirect("/")