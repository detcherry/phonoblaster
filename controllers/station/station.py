from datetime import datetime
from datetime import timedelta
from time import gmtime
from calendar import timegm
from random import randrange

from controllers.station.root import *

from google.appengine.api import channel


class StationHandler(RootStationHandler):
	def get(self, station_id):
		self.current_station = Station.all().filter("identifier", station_id).get()
		
		if not self.current_station:
			self.error(404)
		else:
			self.getChannelAndToken()
			
			self.additional_template_values = {
				"site_url": controllers.config.SITE_URL,
				"channel_id": self.channel_id,
				"token": self.token,
				"allowed_to_post": self.allowed_to_post,
				"status_creator": self.status_creator,
			}		
			self.render("../../templates/station/station.html")
	
	def getChannelAndToken(self):
		
		query = Session.all()
		
		# We retrieve the latest sessions whose channel API token is not expired (3600 sec ~ 1h) / NB: tokens expired after 2 hours
		query.filter("created >", datetime.now() - timedelta(0,3600))
		last_sessions = query.filter("station", self.current_station.key())
		
		session_closed = None
		for session in last_sessions:
			if(session.ended != None):
				session_closed = session
				
				logging.info("We reuse an old channel_id and token")			

				self.channel_id = session_closed.channel_id
				self.token = session_closed.channel_token

				session_closed.ended = None
				session_closed.user = self.current_user
				session_closed.put()
				break
		
		if not session_closed:
			logging.info("There is no old channel_id or token to reuse")
			self.createChannel()
	
	
	def createChannel(self):
		time_now = str(timegm(gmtime()))
		random_integer = str(randrange(1000))
		self.channel_id = time_now + random_integer
		self.token = channel.create_channel(self.channel_id)
				
		session = Session(
			channel_id = self.channel_id,
			channel_token = self.token,
			station = self.current_station,
			user = self.current_user,
		)
		session.put()	
				

application = webapp.WSGIApplication([
	(r"/(\w+)", StationHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()