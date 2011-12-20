import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

import logging	
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler
from controllers.all import AllHandler
from controllers.station.create import StationCreateHandler
from controllers.station.check import StationCheckHandler
from controllers.station.confirm import StationConfirmHandler

application = webapp.WSGIApplication(
	[
		('/', HomeHandler),
		('/station/create', StationCreateHandler),
		('/station/check', StationCheckHandler),
		('/.*', AllHandler),
	],
    debug=True)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()