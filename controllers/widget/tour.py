from controllers.base import *

class WidgetTourHandler(BaseHandler):
	def get(self):
		self.additional_template_values = {};
		self.render("../templates/widget/tour.html")
		

application = webapp.WSGIApplication([
	(r"/widget/tour", WidgetTourHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()