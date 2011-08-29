import os

from django.utils import simplejson

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from models.queue import Queue

class AddController(webapp.RequestHandler):
	def get(self):
		self.redirect("/")
	
	def post(self):
		title = self.request.get("title")
		id = self.request.get("id")
		thumbnail = self.request.get("thumbnail")
		duration = self.request.get("duration")
		
		nonExpiredTracks = Queue.getNonExpiredTracks()
		numberOfNonExpiredTracks = len(nonExpiredTracks)
		
		if(numberOfNonExpiredTracks == 10):
			self.response.out.write(simplejson.dumps({"status":"notAdded"}))
		else:
			Queue.addToQueue(title, id, thumbnail, duration)
			self.response.out.write(simplejson.dumps({"status":"added"}))

application = webapp.WSGIApplication([
	("/add", AddController),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()