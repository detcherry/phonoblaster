from controllers.base import BaseHandler

class JobsHandler(BaseHandler):
	def get(self):
		self.render("company/jobs.html", None)
	