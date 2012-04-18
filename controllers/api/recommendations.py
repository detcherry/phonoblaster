import django_setup
from django.utils import simplejson as json

from controllers.base import BaseHandler
from controllers.base import login_required

from models.api.user import UserApi
from models.db.youtube import Youtube

class ApiRecommendationsHandler(BaseHandler):
	@login_required
	def get(self):
		yt = self.request.get("youtube_ids")
		youtube_ids = yt.split(",")			 

		raw_extended_tracks = Youtube.get_extended_tracks(youtube_ids)
		extended_tracks = []
		for e in raw_extended_tracks:
			if e is not None and e["music"]:
				extended_tracks.append(e)
	
		self.response.out.write(json.dumps(extended_tracks))
		
		
		

		