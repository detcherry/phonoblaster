from datetime import datetime
from calendar import timegm
from django.utils import simplejson

from controllers.base import *

from models.db.track import Track

class PlaylistLatestHandler(BaseHandler):
	@login_required
	def post(self):
		tracks_per_page = 20
		seconds_since_epoch = int(self.request.get("date_limit"))
		date_limit = datetime.utcfromtimestamp(seconds_since_epoch)
		
		# Retrieve the latest tracks after the date_limit
		q = Track.all()
		q.filter("submitter", self.current_user.key())
		q.filter("expired <", date_limit)
		q.order("-expired")
		self.tracks = q.fetch(tracks_per_page + 1)
		
		# Check if additional tracks
		if(len(self.tracks) == tracks_per_page + 1):
			new_date_limit = timegm(self.tracks[-2].expired.utctimetuple())
		else:
			new_date_limit = None
		self.tracks = self.tracks[:tracks_per_page]
		
		output =[]
		for track in self.tracks:
			output.append({
				"id": track.youtube_id,
				"title": track.youtube_title,
				"thumbnail": track.youtube_thumbnail_url,
				"duration": track.youtube_duration,
			})
		data = {
			"date_limit": new_date_limit,
			"tracks": output,
		}
		
		self.response.out.write(simplejson.dumps(data));
		

		
application = webapp.WSGIApplication([
	(r"/playlist/latest", PlaylistLatestHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()