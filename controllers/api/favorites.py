import logging
from datetime import datetime
from django.utils import simplejson as json

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.track import Track

from models.api.station import StationApi

class ApiFavoritesHandler(BaseHandler):
	@login_required
	def get(self):
		offset = datetime.utcfromtimestamp(int(self.request.get("offset")))
		extended_favorites = self.user_proxy.get_favorites(offset)
		self.response.out.write(json.dumps(extended_favorites))
	
	@login_required
	def post(self):
		content = json.loads(self.request.get("content"))
		shortname = self.request.get("shortname")
		station_proxy = StationApi(shortname)
		station = station_proxy.station
		
		response = False;
		if(content["track_id"]):
			track = Track.get_by_id(int(content["track_id"]))
			
			# Check if the track exists on Phonoblaster
			if(track):
				
				# Check if the track exists on Youtube
				extended_track = Track.get_extended_tracks([track])[0]
				
				if(extended_track):
					self.user_proxy.add_to_favorites(track, extended_track, station)
					response = True;
		
		self.response.out.write(json.dumps({ "response": response }))
					

class ApiFavoritesDeleteHandler(BaseHandler):
	
	@login_required
	def delete(self, id):
		track = Track.get_by_id(int(id))
		
		response = False
		if(track):
			self.user_proxy.delete_from_favorites(track) 
			response = True
			
		self.response.out.write(json.dumps({ "response": response }))
				
		
		
		
		
		
