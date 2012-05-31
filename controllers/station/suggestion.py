import re
import logging

from controllers.station.root import RootHandler
from models.db.suggestion import Suggestion
from models.api.station import StationApi

class SuggestionHandler(RootHandler):
	def get(self, key_name):
		suggestion = Suggestion.get_by_key_name(key_name)
		
		if(suggestion):
			m = re.match(r"(\w+).(\w+)", key_name)
			shortname = m.group(1)
			self.station_proxy = StationApi(shortname)
			
			user_agent = self.request.headers["User-Agent"]
			facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
			
			if(user_agent != facebook_agent):
				# Redirect to station
				self.redirect("/" + shortname)
			else:
				# Facebook linter 
				suggestions = [suggestion]
				extended_suggestions = Suggestion.get_extended_suggestions(suggestions)				
				template_values = {
					"suggestion": extended_suggestions[0],
				}
			
				self.render("station/facebook/suggestion.html", template_values)
		else:
			# 404 error
			self.render("station/404.html", None)
