from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler
from controllers.all import AllHandler
from controllers.admin.dashboard import AdminDashboardHandler
from controllers.profile import ProfileHandler
from controllers.station.create import StationCreateHandler
from controllers.station.check import StationCheckHandler
from controllers.station.station import StationHandler
from controllers.station.picture import StationPictureHandler
from controllers.station.broadcast import BroadcastHandler
from controllers.station.track import TrackHandler
from controllers.station.suggestion import SuggestionHandler
from controllers.station.page import StationPageHandler
from controllers.api.queue import ApiQueueHandler
from controllers.api.queue import ApiQueueDeleteHandler
from controllers.api.suggestions import ApiSuggestionsHandler
from controllers.api.favorites import ApiFavoritesHandler
from controllers.api.favorites import ApiFavoritesDeleteHandler
from controllers.api.tracks import ApiTracksHandler
from controllers.api.broadcasts import ApiBroadcastsHandler
from controllers.api.sessions import ApiSessionsHandler
from controllers.api.comments import ApiCommentsHandler
from controllers.api.recommendations import ApiRecommendationsHandler
from controllers.api.views import ApiViewsHandler
from controllers.api.air import ApiAirHandler
from controllers.api.now import ApiNowHandler
from controllers.company.company import JobsHandler

application = webapp.WSGIApplication(
	[
		('/api/queue', ApiQueueHandler),
		('/api/queue/([\w.]+)', ApiQueueDeleteHandler),
		('/api/suggestions', ApiSuggestionsHandler),
		('/api/favorites', ApiFavoritesHandler),
		('/api/favorites/(\w+)', ApiFavoritesDeleteHandler),
		('/api/tracks', ApiTracksHandler),
		('/api/broadcasts', ApiBroadcastsHandler),
		('/api/sessions', ApiSessionsHandler),
		('/api/comments', ApiCommentsHandler),
		('/api/recommendations', ApiRecommendationsHandler),
		('/api/air', ApiAirHandler),
		('/api/views', ApiViewsHandler),
		('/api/now', ApiNowHandler),
		('/admin/dashboard', AdminDashboardHandler),
		('/', HomeHandler),
		('/station/create', StationCreateHandler),
		('/station/check', StationCheckHandler),
		('/(\w+)', StationHandler),
		('/(\w+)/picture', StationPictureHandler),
		('/broadcast/([\w.]+)', BroadcastHandler),
		('/track/([0-9]+)', TrackHandler),
		('/suggestion/([\w.]+)', SuggestionHandler),
		('/station/page', StationPageHandler),
		('/user/([0-9]+)', ProfileHandler),
		('/company/jobs', JobsHandler),
		('/.*', AllHandler),
	],
    debug=True
)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()