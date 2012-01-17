import logging
from datetime import datetime
from django.utils import simplejson as json

from controllers import config
from controllers.base import BaseHandler
from controllers.base import login_required

from models.db.favorite import Favorite
from models.db.track import Track

class ApiFavoritesHandler(BaseHandler):
	@login_required
	def get(self):
		offset = datetime.utcfromtimestamp(int(self.request.get("offset")))
		self.user = self.user_proxy.user
		
		q = Favorite.all()
		q.filter("user", self.user.key())
		q.filter("created <", offset)
		q.order("-created")
		favorites = q.fetch(2) # Arbitrary number
		
		extended_favorites = Favorite.get_extended_favorites(favorites)
		self.response.out.write(json.dumps(extended_favorites))
	
	@login_required
	def post(self):
		content = json.loads(self.request.get("content"))
		self.user = self.user_proxy.user
		
		response = False;
		if(content["track_id"]):
			track = Track.get_by_id(int(content["track_id"]))
			
			if(track):
				# Check if the favorite hasn't been stored yet
				q = Favorite.all()
				q.filter("user", self.user.key())
				q.filter("track", track.key())
				existing_favorite = q.get()
				
				if(existing_favorite):
					logging.info("Track already favorited by this user")
				else:	
					favorite = Favorite(
						track = track.key(),
						user = self.user.key(),
					)
					favorite.put()
					logging.info("Favorite saved into datastore")
			
					self.user_proxy.increment_favorites_counter()
					logging.info("Favorite counter incremented")
			
				response = True
		
		self.response.out.write(json.dumps({ "response": response }))


class ApiFavoritesDeleteHandler(BaseHandler):
	
	@login_required
	def delete(self, id):
		self.user = self.user_proxy.user
		track = Track.get_by_id(int(id))
		
		response = False
		if(track):
			q = Favorite.all()
			q.filter("user", self.user.key())
			q.filter("track", track.key()) 
			favorite = q.get()
			
			if favorite is None:
				logging.info("This track has never been favorited by this user")
			else:
				favorite.delete()
				logging.info("Favorite deleted from datastore")
				
				self.user_proxy.decrement_favorites_counter()
				logging.info("Favorite counter decremented")
			
			response = True
		
		self.response.out.write(json.dumps({ "response": response }))
				
		
		
		
		
		
