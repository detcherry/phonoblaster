import logging
import json
from datetime import datetime

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.track import Track

from models.api.station import StationApi

class ApiLikesHandler(BaseHandler):
	def get(self):
		shortname = self.request.get("shortname")
		offset = self.request.get("offset")
		
		host_proxy = StationApi(shortname)
		host = host_proxy.station

		if(host and offset):
			extended_likes = host_proxy.get_likes(datetime.utcfromtimestamp(int(offset)))
			self.response.out.write(json.dumps(extended_likes))
		else:
			self.error(404)
	
	@login_required
	def post(self):
		content = json.loads(self.request.get("content"))
		
		response = False;
		if(content["track_id"]):
			track = Track.get_by_id(int(content["track_id"]))
			
			# Check if the track exists on Phonoblaster
			if(track):
				profile = self.user_proxy.profile
				profile_proxy = StationApi(profile["shortname"])
				profile_proxy.add_to_likes(track)
				response = True
		
		self.response.out.write(json.dumps({ "response": response }))
					

class ApiLikesDeleteHandler(BaseHandler):
	
	@login_required
	def delete(self, id):
		track = Track.get_by_id(int(id))
		
		response = False
		if(track):
			profile = self.user_proxy.profile
			profile_proxy = StationApi(profile["shortname"])
			profile_proxy.add_to_likes(track)
			response = True
			
		self.response.out.write(json.dumps({ "response": response }))