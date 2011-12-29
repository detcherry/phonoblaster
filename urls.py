import os
from google.appengine.dist import use_library
use_library('django', '1.2')
from django.conf import settings
settings.configure(INSTALLED_APPS=('settings',))

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler
from controllers.all import AllHandler
from controllers.station.create import StationCreateHandler
from controllers.station.check import StationCheckHandler
from controllers.station.station import StationHandler
from controllers.station.broadcasts import StationBroadcastsHandler
from controllers.presence.request import PresenceRequestHandler
from controllers.api.queue import GetQueueHandler
from controllers.api.presences import GetPresencesHandler

application = webapp.WSGIApplication(
	[
		('/', HomeHandler),
		('/station/create', StationCreateHandler),
		('/station/check', StationCheckHandler),
		('/(\w+)', StationHandler),
		('/(\w+)/broadcasts', StationBroadcastsHandler),
		('/(\w+)/presence/request', PresenceRequestHandler),
		('/api/queue', GetQueueHandler),
		('/api/presences', GetPresencesHandler),
		('/.*', AllHandler),
	],
    debug=True
)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()