import os
import logging

from google.appengine.dist import use_library
use_library('django', '1.2')
from django.conf import settings
settings.configure(INSTALLED_APPS=('settings',))

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler
from controllers.all import AllHandler
from controllers.station.create import StationCreateHandler
from controllers.station.check import StationCheckHandler
from controllers.station.station import StationHandler
from controllers.station.broadcasts import StationBroadcastsHandler
from controllers.api.queue import ApiQueueHandler
from controllers.api.presences import ApiPresencesHandler
from controllers.api.comments import ApiCommentsHandler
from controllers.api.now import ApiNowHandler

application = webapp.WSGIApplication(
	[
		('/', HomeHandler),
		('/station/create', StationCreateHandler),
		('/station/check', StationCheckHandler),
		('/(\w+)', StationHandler),
		('/(\w+)/broadcasts', StationBroadcastsHandler),
		('/api/queue', ApiQueueHandler),
		('/api/presences', ApiPresencesHandler),
		('/api/comments', ApiCommentsHandler),
		('/api/now', ApiNowHandler),
		('/.*', AllHandler),
	],
    debug=True
)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()