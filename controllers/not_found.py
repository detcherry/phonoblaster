from controllers.base import *

class NotFoundHandler(BaseHandler):
	def get(self):
		print "not found"

application = webapp.WSGIApplication([
	(r"/.*", NotFoundHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()