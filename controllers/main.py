import os, logging

from django.utils import simplejson
from datetime import datetime

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from models.queue import Queue

class MainController(webapp.RequestHandler):
	def get(self):
		lastRequestTime = datetime.now();
		tracksInTheQueue = Queue.getNonExpiredTracks()
		
		path = os.path.join(os.path.dirname(__file__), '../templates/main.html')
		self.response.out.write(template.render(path, {
			"tracksInTheQueue": tracksInTheQueue,
			"lastRequestTime": lastRequestTime,
		}))
	
	def post(self):
		lastSongAdditionTime = self.request.get("addition_time")
		
		newTracksInTheQueue = Queue.getNewNonExpiredTracks(lastSongAdditionTime)
		
		response = { "tracks": [] }

		if(newTracksInTheQueue):
			for track in newTracksInTheQueue:
				
				JSON_addition_time = str(track.addition_time)
				JSON_expiration_time = str(track.expiration_time)
				
				response["tracks"].append({
					"title":track.youtube_title,
					"id": track.youtube_id,
					"thumbnail": track.youtube_thumbnail_url,
					"duration":track.youtube_duration,
					"addition_time": JSON_addition_time,
					"expiration_time": JSON_expiration_time,
				})
		
		self.response.out.write(simplejson.dumps(response))		

application = webapp.WSGIApplication([
	("/.*", MainController),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()