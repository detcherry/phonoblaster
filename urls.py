import logging

try:
	from google.appengine.dist import use_library
	use_library('django', '1.2')
except:
	logging.info("Older django version seems to be reluctant...")

try:	
	from django.conf import settings
	settings.configure(INSTALLED_APPS=('empty',))
except RuntimeError:
	logging.info("Runtime has already been set up with django 1.2")
	
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler

application = webapp.WSGIApplication(
	[
		('/', HomeHandler),
		# !!!! write a global handler
	],
    debug=True)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()