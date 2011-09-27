from controllers.base import *

class LoginHandler(BaseHandler):
	def get(self):
		if(self.current_user):
			redirectUrl = self.request.get("redirect_url")
			if(redirectUrl):
				self.redirect(redirectUrl)
			else:
				self.redirect("/")
		else:
			self.additional_template_values = {}
			self.render("../templates/account/login.html")

application = webapp.WSGIApplication([
	(r"/account/login", LoginHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()