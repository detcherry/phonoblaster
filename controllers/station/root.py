from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution
from models.db.track import Track
from models.db.session import Session
from models.db.counter import *

class RootStationHandler(BaseHandler):
	
	@property
	def status_creator(self):
		if not hasattr(self, "_status_creator"):
			self._status_creator = False
			if(self.current_user):
				if(self.current_user.key() == self.current_station.creator.key()):
					self._status_creator = True
		return self._status_creator
	
	@property
	def current_contributions(self):
		if not hasattr(self, "_current_contributions"):
			current_station_contributions = Contribution.all().filter("station", self.current_station.key()).fetch(10)
			user_keys = [Contribution.contributor.get_value_for_datastore(c) for c in current_station_contributions]
			current_station_contributors = db.get(user_keys)
			self._current_contributions = zip(current_station_contributions, current_station_contributors)
		return self._current_contributions
	
	@property
	def allowed_to_post(self):
		if not hasattr(self, "_allowed_to_post"):
			self._allowed_to_post = False;
			if(self.current_user):	
				if(self.current_station.creator.key() == self.current_user.key()):
					self._allowed_to_post = True
				else:
					contributor = Contribution.all().filter("station", self.current_station.key()).filter("contributor", self.current_user.key()).get()
					if(contributor):
						self._allowed_to_post = True
		return self._allowed_to_post
	
	@property
	def number_of_tracks(self):
		if not hasattr(self, "_number_of_tracks"):
			counter_name = "tracks_counter_station_" + str(self.current_station.key().id())
			
			#Transition_code
			number_of_tracks_in_the_counter = GeneralCounterShardConfig.get_count(counter_name)
			logging.info(number_of_tracks_in_the_counter)
			real_number = Track.all().filter("station", self.current_station.key()).count()
			logging.info(real_number)
			if(number_of_tracks_in_the_counter != real_number):
				GeneralCounterShardConfig.init(counter_name, real_number)

			self._number_of_tracks = GeneralCounterShardConfig.get_count(counter_name)
			
			#Old Code
			#self._number_of_tracks = Track.all().filter("station", self.current_station.key()).count()
		return self._number_of_tracks
	
	
	def render(self, template_path):
		path = os.path.join(os.path.dirname(__file__), template_path)		
		
		# Standard values that are added to the station.py, tracks.py, contributors.py handlers
		self.additional_template_values["current_station"] = self.current_station
		self.additional_template_values["number_of_tracks"] = self.number_of_tracks
		self.additional_template_values["current_contributions"] = self.current_contributions
		self.additional_template_values["number_of_contributions"] = len(self.additional_template_values["current_contributions"]) + 1		
		
		self.response.out.write(template.render(path, self.template_values))
		
		