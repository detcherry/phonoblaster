import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from models.db.counter import Shard

class CounterHandler(webapp.RequestHandler):
	def post(self):
		shard_name = self.request.get("shard_name")
		method = self.request.get("method")
		
		if(method == "increment"):
			Shard.increment(shard_name)
		else:
			Shard.decrement(shard_name)

		
application = webapp.WSGIApplication([
	(r"/taskqueue/counter", CounterHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()	