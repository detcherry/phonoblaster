import logging
import webapp2

from google.appengine.api import mail

class MailHandler(webapp2.RequestHandler):
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