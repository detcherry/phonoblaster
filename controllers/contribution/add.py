from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution
from models.db.request import FcbkRequest

class AddContributionHandler(BaseHandler):
	@login_required
	def post(self):
		station_id = self.request.get("station_id")
		self.station = Station.all().filter("identifier", station_id).get()	
		self.request_ids = self.request.get("request_ids").split(",")
		
		if(self.isStationCreator()):
			self.storeRequests()
			self.getExistingContributors()			
			self.getInvitees()
			self.getNewContributors()
			self.limitContributorsTo10()
			self.storeNewContributors()
		else:
			self.error(403)
	
	def isStationCreator(self):
		if(self.station.creator.key() == self.current_user.key()):
			return True
		else:
			return False
	
	def storeRequests(self):		
		for request_id in self.request_ids:
			fcbkRequest = FcbkRequest(
				fcbk_id = request_id,
				requester = self.current_user.key(),
				station = self.station.key(),
			)
			fcbkRequest.put()

	def getExistingContributors(self):
		self.existing_contributors = []
		existing_contributions = Contribution.all().filter("station", self.station.key())
		
		for contribution in existing_contributions:
			self.existing_contributors.append(contribution.contributor.facebook_id)
		
		logging.info("Existing contributors: %s" % (self.existing_contributors))
	
	def getInvitees(self):
		self.invitees = []
		cookie = controllers.facebook.get_user_from_cookie(
			self.request.cookies,
			controllers.config.FACEBOOK_APP_ID,
			controllers.config.FACEBOOK_APP_SECRET
		)
		self.graph = controllers.facebook.GraphAPI(cookie["access_token"])
		requests = self.graph.get_objects(self.request_ids)		
		
		for request_id in self.request_ids:
			self.invitees.append(str(requests[request_id]["to"]["id"]))
		
		logging.info("Invitees via Facebook: %s" % (self.invitees))
	
	def getNewContributors(self):
		self.new_contributors = []
		for contributor in self.existing_contributors:
			for invitee in self.invitees:
				if(invitee == contributor):
					self.invitees.remove(invitee)
					break
		self.new_contributors = self.invitees
		
		logging.info("New contributors: %s" %(self.new_contributors))
		
	def limitContributorsTo10(self):
		number_of_contributors_left = 10 - len(self.existing_contributors)
		number_of_new_contributors_to_eject = len(self.new_contributors) - number_of_contributors_left
		if(number_of_new_contributors_to_eject > 0):
			for i in range(0, number_of_new_contributors_to_eject):
				self.new_contributors.pop()

	def storeNewContributors(self):
		if(self.new_contributors):
			#First we handle the users that are already on phonoblaster
			phonoblaster_users = User.all().filter("facebook_id IN", self.new_contributors)			
			for phonoblaster_user in phonoblaster_users:
				#We store the new contribution
				contribution = Contribution(
					contributor = phonoblaster_user.key(),
					station = self.station.key(),
				)
				contribution.put()
				logging.info("Contribution saved for an existing phonoblaster user: %s" %(phonoblaster_user.name))
				#We widthdraw the the facebook id from the list of new contributors
				self.new_contributors.remove(phonoblaster_user.facebook_id)
		
		if(self.new_contributors):
			#Second, we handle the users that are only on facebook
			facebook_users = self.graph.get_objects(self.new_contributors)
			for user_id in facebook_users:
				#We store the new user
				user = User(
					facebook_id = user_id,
					name = facebook_users[user_id]["name"],
					first_name = facebook_users[user_id]["first_name"],
					last_name = facebook_users[user_id]["last_name"],
					public_name = facebook_users[user_id]["first_name"] + " " + facebook_users[user_id]["last_name"][0] +".",
				)
				user.put()
				logging.info("New phonoblaster user saved: %s" %(user.name))
				#We store the new contribution
				contribution = Contribution(
					contributor = user.key(),
					station = self.station.key()
				)
				contribution.put()
				logging.info("New contribution saved for the user that has just been saved")
		


application = webapp.WSGIApplication([
	(r"/contribution/add", AddContributionHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()