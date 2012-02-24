from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.api.user import UserApi

class FriendsHandler(webapp.RequestHandler):
	def post(self):
		user_key_name = self.request.get("key_name")
		user_proxy = UserApi(user_key_name)
		user_proxy.save_friends()


application = webapp.WSGIApplication([
	(r"/taskqueue/friends", FriendsHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
