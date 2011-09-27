from controllers.base import *

from calendar import timegm
from django.utils import simplejson

from models.db.message import Message
from models.db.station import Station
from models.notifiers.message import MessageNotifier

from google.appengine.api import quota

class AddMessageHandler(BaseHandler):
	@login_required
	def post(self):
		self.text = self.request.get("text")
		self.station_key = self.request.get("station_key")
		self.channel_id = self.request.get("channel_id")
		
		self.station = Station.get(self.station_key)
		
		#We don't check if the user is really in this station. We only check if the station exists.
		if(self.station):
			self.message = Message(
				author = self.current_user.key(),
				text = self.text,
				station = self.station.key(),
			)
			self.message.put()			
			logging.info("Message sent by %s in the %s station has been saved" % (self.current_user.public_name, self.station.identifier))			
			
			messageNotifier = MessageNotifier(self.station, self.message, self.channel_id)
			self.response.out.write(simplejson.dumps({"status":"Added"}))			
		else:
			self.error(404)



application = webapp.WSGIApplication([
	(r"/message/add", AddMessageHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()