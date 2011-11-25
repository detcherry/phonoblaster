from controllers.broadcaster.root import RootHandler
from models.api.user import UserApi

class BroadcasterHandler(RootHandler):
	def get(self, broadcaster_username):
		self.broadcaster_proxy = UserApi(broadcaster_username)
		self.current_broadcaster = self.broadcaster_proxy.user
		if self.current_broadcaster:
			self.root_render("broadcaster/broadcaster.html", None)
		else:
			self.root_render("broadcaster/notfound.html", None)