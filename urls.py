from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler
from controllers.all import AllHandler
from controllers.station.create import StationCreateHandler
from controllers.station.check import StationCheckHandler
from controllers.station.station import StationHandler
from controllers.station.picture import StationPictureHandler
from controllers.station.broadcasts import StationBroadcastsHandler
from controllers.station.track import TrackHandler
from controllers.api.queue import ApiQueueHandler
from controllers.api.queue import ApiQueueDeleteHandler
from controllers.api.suggestions import ApiSuggestionsHandler
from controllers.api.favorites import ApiFavoritesHandler
from controllers.api.favorites import ApiFavoritesDeleteHandler
from controllers.api.library import ApiLibraryHandler
from controllers.api.recommandations import ApiRecommandationsHandler
from controllers.api.broadcasts import ApiBroadcastsHandler
from controllers.api.presences import ApiPresencesHandler
from controllers.api.comments import ApiCommentsHandler
from controllers.api.views import ApiViewsHandler
from controllers.api.status import ApiStatusHandler
from controllers.api.now import ApiNowHandler

application = webapp.WSGIApplication(
	[
		('/api/queue', ApiQueueHandler),
		('/api/queue/([\w.]+)', ApiQueueDeleteHandler),
		('/api/suggestions', ApiSuggestionsHandler),
		('/api/favorites', ApiFavoritesHandler),
		('/api/favorites/(\w+)', ApiFavoritesDeleteHandler),
		('/api/library', ApiLibraryHandler),
		('/api/recommandations', ApiRecommandationsHandler),
		('/api/broadcasts', ApiBroadcastsHandler),
		('/api/presences', ApiPresencesHandler),
		('/api/comments', ApiCommentsHandler),
		('/api/status', ApiStatusHandler),
		('/api/views', ApiViewsHandler),
		('/api/now', ApiNowHandler),
		('/', HomeHandler),
		('/station/create', StationCreateHandler),
		('/station/check', StationCheckHandler),
		('/(\w+)', StationHandler),
		('/(\w+)/picture', StationPictureHandler),
		('/(\w+)/broadcasts', StationBroadcastsHandler),
		('/track/([0-9]+)', TrackHandler),
		('/.*', AllHandler),
	],
    debug=True
)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()