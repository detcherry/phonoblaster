from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from controllers.home import HomeHandler
from controllers.all import AllHandler
from controllers.admin.dashboard import AdminDashboardHandler
from controllers.admin.upgrade import UpgradeHandler
from controllers.buffer_test import BufferHandler
from controllers.profile import ProfileInitHandler
from controllers.profile import ProfileSwitchHandler
from controllers.station.manage import StationManageHandler
from controllers.station.check import StationCheckHandler
from controllers.station.station import StationHandler
from controllers.station.picture import StationPictureHandler
from controllers.station.broadcast import BroadcastHandler
from controllers.station.track import TrackHandler
from controllers.station.suggestion import SuggestionHandler
from controllers.station.page import StationPageHandler
from controllers.api.buffer import ApiBufferHandler
from controllers.api.buffer import ApiBufferDeleteHandler
from controllers.api.suggestions import ApiSuggestionsHandler
from controllers.api.likes import ApiLikesHandler
from controllers.api.likes import ApiLikesDeleteHandler
from controllers.api.tracks import ApiTracksHandler
from controllers.api.tracks import ApiTracksDeleteHandler
from controllers.api.broadcasts import ApiBroadcastsHandler
from controllers.api.sessions import ApiSessionsHandler
from controllers.api.recommendations import ApiRecommendationsHandler
from controllers.api.now import ApiNowHandler
from controllers.company.company import TermsHandler
from controllers.company.company import FaqHandler
from controllers.company.company import PressHandler
from controllers.company.company import PressFrHandler

application = webapp.WSGIApplication(
	[
		('/api/buffer',ApiBufferHandler),
		('/api/buffer/([\w.]+)', ApiBufferDeleteHandler),
		('/api/suggestions', ApiSuggestionsHandler),
		('/api/likes', ApiLikesHandler),
		('/api/likes/(\w+)', ApiLikesDeleteHandler),
		('/api/tracks', ApiTracksHandler),
		('/api/tracks/([\w.]+)', ApiTracksDeleteHandler),
		('/api/broadcasts', ApiBroadcastsHandler),
		('/api/sessions', ApiSessionsHandler),
		('/api/recommendations', ApiRecommendationsHandler),
		('/api/now', ApiNowHandler),
		('/admin/dashboard', AdminDashboardHandler),
		('/admin/upgrade', UpgradeHandler),
		('/', HomeHandler),
		('/station/manage', StationManageHandler),
		('/station/check', StationCheckHandler),
		('/(\w+)', StationHandler),
		('/(\w+)/picture', StationPictureHandler),
		('/broadcast/([\w.]+)', BroadcastHandler),
		('/profile/init', ProfileInitHandler),
		('/profile/switch/([0-9]+)', ProfileSwitchHandler),
		('/track/([0-9]+)', TrackHandler),
		('/suggestion/([\w.]+)', SuggestionHandler),
		('/station/page', StationPageHandler),
		('/company/terms', TermsHandler),
		('/company/faq', FaqHandler),
		('/company/press', PressHandler),
		('/company/press/fr', PressFrHandler),
		('/.*', AllHandler),
	],
    debug=True
)

def main(): 
	run_wsgi_app(application)

if __name__ == '__main__':
    main()