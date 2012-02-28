import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import mail

class MailHandler(webapp.RequestHandler):
	def post(self):
		to = self.request.get("to")
		subject = self.request.get("subject")
		body = self.request.get("body")

		email = mail.EmailMessage(
			sender = "Damien <damien@phonoblaster.com>",
			to = to,
			subject = subject,
			body = body,
		)
		
		email.send()
		logging.info("Mail sent")

application = webapp.WSGIApplication([
	(r"/taskqueue/mail", MailHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()