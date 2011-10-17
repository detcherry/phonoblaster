from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution
from models.db.request import FcbkRequest
from models.interface.station import InterfaceStation

class AddContributionHandler(BaseHandler):
	@login_required
	def post(self):
		station_key = self.request.get("station_key")
		self.request_id = self.request.get("request_id")
		self.invitees = self.request.get("recipient_ids").split(",")
		
		# The proxy will allow us to retrieve and add contributors consistently with the memcache
		self.station_proxy = InterfaceStation(station_key = station_key)
		self.station = self.station_proxy.station
		
		if(self.is_station_creator()):
			self.store_facebook_request()
			self.insert_or_get_contributors()
		else:
			self.error(403)
	
	def is_station_creator(self):
		return self.station_proxy.is_creator(self.current_user.key())
	
	def store_facebook_request(self):		
		fcbkRequest = FcbkRequest(
			fcbk_id = self.request_id,
			requester = self.current_user.key(),
			station = self.station.key(),
		)
		fcbkRequest.put()

	def insert_or_get_contributors(self):
		self.new_contributors = self.invitees[0:9]
		phonoblaster_contributors = []
		facebook_contributors = []

		if(self.new_contributors):
			#First we handle the users that are already on phonoblaster
			phonoblaster_contributors = User.all().filter("facebook_id IN", self.new_contributors).fetch(10)		
			#We widthdraw the the facebook id from the list of new contributors
			for user in phonoblaster_contributors:
				self.new_contributors.remove(user.facebook_id)
		
		# If there are some people left, that means they're only on Facebook (for the moment)
		if(self.new_contributors):
			cookie = controllers.facebook.get_user_from_cookie(
				self.request.cookies,
				controllers.config.FACEBOOK_APP_ID,
				controllers.config.FACEBOOK_APP_SECRET
			)
			self.graph = controllers.facebook.GraphAPI(cookie["access_token"])
			facebook_users = self.graph.get_objects(self.new_contributors)
			for user_id in facebook_users:
				#We store the new user
				new_user = User(
					facebook_id = user_id,
					name = facebook_users[user_id]["name"],
					first_name = facebook_users[user_id]["first_name"],
					last_name = facebook_users[user_id]["last_name"],
					public_name = facebook_users[user_id]["first_name"] + " " + facebook_users[user_id]["last_name"][0] +".",
				)
				facebook_contributors.append(new_user)

			# We save them in bulk in the datastore
			db.put(facebook_contributors)
			logging.info("Facebook users invited to contribute are now pseudo phonoblaster users: they're partially in the datastore")

		# Now that we only have Phonoblaster users, we pass them to the station proxy (will handle memcache and datastore)
		all_contributors = phonoblaster_contributors + facebook_contributors
		self.station_proxy.add_contributors(all_contributors)


application = webapp.WSGIApplication([
	(r"/contribution/add", AddContributionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()