from datetime import datetime
from datetime import timedelta
from calendar import timegm
from time import gmtime
from random import randrange
from django.utils import simplejson

from controllers.base import *

from models.interface.station import InterfaceStation

class ChannelRequestHandler(BaseHandler):
	def post(self):
		station_key = self.request.get("station_key")
		station_proxy = InterfaceStation(station_key = station_key)
		
		new_session = None
		if(self.current_user):
			new_session = station_proxy.add_session(user_key = self.current_user.key())
		else:
			new_session = station_proxy.add_session()
		
		output = {
			"channel_id": new_session.channel_id,
			"token": new_session.channel_token,
		}
		self.response.out.write(simplejson.dumps(output))
	

application = webapp.WSGIApplication([
	(r"/channel/request", ChannelRequestHandler),
], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
    main()
