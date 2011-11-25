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

from controllers import base
from controllers.home import HomeHandler
from controllers.oauth.login import TwitterLoginHandler
from controllers.oauth.request import TwitterRequestHandler
from controllers.oauth.authorize import TwitterAuthorizeHandler
from controllers.oauth.close import TwitterCloseHandler
from controllers.oauth.cleanup import TwitterCleanupHandler
from controllers.oauth.logout import TwitterLogoutHandler

application = webapp.WSGIApplication(
	[
		('/', HomeHandler),
		('/oauth/login', TwitterLoginHandler),
		('/oauth/request', TwitterRequestHandler),
		('/oauth/authorize', TwitterAuthorizeHandler),
		('/oauth/close', TwitterCloseHandler),
		('/oauth/cleanup', TwitterCleanupHandler),
		('/oauth/logout', TwitterLogoutHandler),
	],
    debug=True)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()