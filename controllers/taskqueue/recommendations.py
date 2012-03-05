from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.api.user import UserApi

class RecommendationsHandler(webapp.RequestHandler):
	def post(self):
		user_key_name = self.request.get("key_name")
		code = self.request.get("code")
		user_proxy = UserApi(user_key_name, code = code)
		user_proxy.save_recommendations()


application = webapp.WSGIApplication([
	(r"/taskqueue/recommendations", RecommendationsHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()