import re

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
			
			extended_suggestion = Suggestion.get_extended_suggestions([suggestion])[0]
			template_values = {
				"suggestion": extended_suggestion,
			}
			self.render("station/suggestion.html", template_values)
			
		else:
			self.render("station/404.html", None)
