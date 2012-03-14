import re
import logging

from controllers.station.secondary import SecondaryHandler
from models.db.suggestion import Suggestion
from models.api.station import StationApi

class SuggestionHandler(SecondaryHandler):
	def get(self, key_name):
		suggestion = Suggestion.get_by_key_name(key_name)
		
		if(suggestion):
			m = re.match(r"(\w+).(\w+)", key_name)
			shortname = m.group(1)
			self.station_proxy = StationApi(shortname)
			
			suggestions = [suggestion]
			extended_suggestions = Suggestion.get_extended_suggestions(suggestions)
			
			if(extended_suggestions):
				logging.info("Youtube track was found")
				
				extended_suggestion = extended_suggestions[0]
				template_values = {
					"suggestion": extended_suggestion,
				}
				
				user_agent = self.request.headers["User-Agent"]
				facebook_agent = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"
			
				if(user_agent == facebook_agent):
					# Facebook linter 
					self.facebook_render("station/facebook/suggestion.html", template_values)
				else:
					# Not facebook linter
					self.render("station/suggestion.html", template_values)

			else:
				logging.info("Youtube track was not found")
				self.redirect("/" + shortname)
			
		else:
			self.render("station/404.html", None)
