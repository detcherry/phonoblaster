from datetime import datetime
from datetime import timedelta
from calendar import timegm
from time import gmtime
from random import randrange
from django.utils import simplejson

from controllers.base import *

from google.appengine.api import channel

from models.db.station import Station
from models.db.session import Session

class ChannelRequestHandler(BaseHandler):
	def post(self):
		station_key = self.request.get("station_key")
		self.current_station =  Station.get(station_key)
		
		if not self.current_station:
			self.error(404)
		else:
			self.getChannelAndToken()
			output = {
				"channel_id": self.channel_id,
				"token": self.token,
			}
			self.response.out.write(simplejson.dumps(output))
		
			
	def getChannelAndToken(self):
		query = Session.all()
		# We retrieve the latest sessions whose channel API token is not expired (3600 sec ~ 1h) / NB: tokens expired after 2 hours
		query.filter("created >", datetime.now() - timedelta(0,3600))
		last_sessions = query.filter("station", self.current_station.key())

		session_closed = None
		for session in last_sessions:
			#If the station has already an end date, we gonna reuse it
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
	(r"/channel/request", ChannelRequestHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
