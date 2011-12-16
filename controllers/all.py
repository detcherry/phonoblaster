from base import BaseHandler

class AllHandler(BaseHandler):
	def get(self):
		# Redirect to homepage in case URL was not found
		self.redirect("/")