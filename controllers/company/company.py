from controllers.base import BaseHandler

class JobsHandler(BaseHandler):
	def get(self):
		self.render("company/jobs.html", None)

class TermsHandler(BaseHandler):
	def get(self):
		self.render("company/terms.html", None)

class FaqHandler(BaseHandler):
	def get(self):
		self.render("company/faq.html", None)
		
class PressHandler(BaseHandler):
	def get(self):
		self.render("company/press.html", None)