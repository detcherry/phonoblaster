import logging
from datetime import datetime
import django_setup
from django.utils import simplejson as json

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.track import Track

from models.api.user import UserApi

class ApiFavoritesHandler(BaseHandler):
	def get(self):
		key_name = self.request.get("key_name")
		offset = self.request.get("offset")
		
		if(key_name and offset):
			profile_proxy = UserApi(key_name) # TO BE CHANGED
			extended_favorites = profile_proxy.get_favorites(datetime.utcfromtimestamp(int(offset)))
			self.response.out.write(json.dumps(extended_favorites))
	
	@login_required
	def post(self):
		content = json.loads(self.request.get("content"))
		
		response = False;
		if(content["track_id"]):
			track = Track.get_by_id(int(content["track_id"]))
			
			# Check if the track exists on Phonoblaster
			if(track):
				self.user_proxy.add_to_favorites(track)
				response = True
		
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