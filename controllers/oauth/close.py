from controllers.base import BaseHandler

# This only brings the popup to close
class TwitterCloseHandler(BaseHandler):
	def get(self):
		self.render("oauth/close.html", None)