from controllers.base import BaseHandler

# Screen for user to log in
class TwitterLoginHandler(BaseHandler):
	def get(self):
		if not self.current_user:
			self.render("oauth/login.html", None)
		else:
			redirect_url = self.request.get("redirect_url")
			if redirect_url:
				# Redirect to the initial page
				self.redirect(redirect_url)
			else:
				# Redirect to homepage
				self.redirect("/")