from controllers.base import *

class NotFoundHandler(BaseHandler):
	def get(self):
		self.additional_template_values = {}
		self.render("../templates/notfound.html")

application = webapp.WSGIApplication([
	(r"/.*", NotFoundHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()