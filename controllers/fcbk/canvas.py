from controllers.base import *

from models.db.request import FcbkRequest

class CanvasHandler(BaseHandler):
	def post(self):
		request_ids = self.request.get("request_ids").split(",")
		self.requests = FcbkRequest.all().order("-created").filter("fcbk_id IN", request_ids)
		
		self.additional_template_values = {
			"requests": self.requests,
			"site_url": controllers.config.SITE_URL
		}
		self.render("../templates/facebook/canvas.html")
	
application = webapp.WSGIApplication([
	(r"/facebook/canvas/", CanvasHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()