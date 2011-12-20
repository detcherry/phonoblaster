import logging
from django.utils import simplejson

from controllers.base import BaseHandler
from controllers.base import login_required
from controllers import config
from controllers import facebook
from controllers.facebook import GraphAPIError

from models.db.station import Station

class StationCreateHandler(BaseHandler):
	@login_required
	def post(self):
		if(self.user_proxy):
			page_id = self.request.get("page_id")
			page_shortname = self.request.get("page_shortname")
			
			page_contribution = self.user_proxy.get_page_contribution(page_id)
			page_access_token = page_contribution["page_access_token"]
			if(page_access_token):
				
				# Init the Facebook library with the page access token
				graph = facebook.GraphAPI(page_access_token)
				
				station_created = False
				try:
					# We put the new tab in the fan page
					station_created = graph.put_object(page_id, "tabs", app_id = config.FACEBOOK_APP_ID)
					
					# If the operation is successful, we store this new station in the datastore
					if station_created:
						station = Station(
							key_name = str(page_id),
							name = str(page_contribution["page_name"]),
						)
						station.put()
						logging.info("New station %s put in the datastore" %(station.name))
						
				except GraphAPIError, e:
					logging.error(e)
				
				self.response.out.write(simplejson.dumps({
					"station_created": station_created,
					#"name_availability": name_availability,
				}))
				
			else:
				self.error(403)
		else:
			self.error(403)
		
		