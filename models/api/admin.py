from models.db.counter import Shard

class AdminApi():
	def __init__(self):
		self._counter_of_users_id = "users"
		self._counter_of_stations_id = "stations"
		
	@property
	def number_of_users(self):
		if not hasattr(self, "_number_of_users"):
			shard_name = self._counter_of_users_id
			self._number_of_users = Shard.get_count(shard_name)
		return self._number_of_users
	
	def increment_users_counter(self):
		shard_name = self._counter_of_users_id
		Shard.task(shard_name, "increment")
	
	@property
	def number_of_stations(self):
		if not hasattr(self, "_number_of_stations"):
			shard_name = self._counter_of_stations_id
			self._number_of_stations = Shard.get_count(shard_name)
		return self._number_of_stations
		
	def increment_stations_counter(self):
		shard_name = self._counter_of_stations_id
		Shard.task(shard_name, "increment")
		