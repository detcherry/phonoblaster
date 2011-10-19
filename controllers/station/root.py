from controllers.base import *

from models.db.user import User
from models.db.station import Station
from models.db.contribution import Contribution
from models.db.track import Track
from models.db.session import Session
from models.db.counter import *

from models.interface.station import InterfaceStation

class RootStationHandler(BaseHandler):
	
	@property
	def status_creator(self):
		if not hasattr(self, "_status_creator"):
			self._status_creator = False
			if(self.current_user):
				if(self.station_proxy.is_creator(str(self.current_user.key()))):
					self._status_creator = True
		return self._status_creator
	
	@property
	def allowed_to_post(self):
		if not hasattr(self, "_allowed_to_post"):
			self._allowed_to_post = False
			if(self.current_user):
				if(self.station_proxy.is_allowed_to_add(str(self.current_user.key()))):
					self._allowed_to_post = True
		return self._allowed_to_post
	
	@property
	def number_of_tracks(self):
		if not hasattr(self, "_number_of_tracks"):
			counter_name = "tracks_counter_station_" + str(self.current_station.key().id())
			self._number_of_tracks = GeneralCounterShardConfig.get_count(counter_name)
		return self._number_of_tracks
	
	@property
	def current_contributors(self):
		if not hasattr(self, "_current_contributors"):
			self._current_contributors = self.station_proxy.station_contributors
		return self._current_contributors
	
	def render(self, template_path):
		path = os.path.join(os.path.dirname(__file__), template_path)		
		
		# Standard values that are added to the station.py, tracks.py, contributors.py handlers
		self.additional_template_values["current_station"] = self.current_station
		self.additional_template_values["number_of_tracks"] = self.number_of_tracks	
		self.additional_template_values["current_contributors"] = self.current_contributors
		self.additional_template_values["number_of_contributions"] = len(self.current_contributors) + 1
		
		self.response.out.write(template.render(path, self.template_values))
		
		