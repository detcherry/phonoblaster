import logging

from google.appengine.api import memcache
from models.db.station import Station
from models.db.contribution import Contribution

class InterfaceStation():
	"""
	
	"""
	def put(creator = None, identifier = None, picture = None, thumbnail = None, website = None, description = None):
		if creator and identifier and picture and thumbnail:
			logging.info("blabla")
		else:
			raise ValueError("A station must have a creator, identifier, picture and thumbnail")
	
	
	
	
	"""
		identifier: str
		returns: db.Model > Station
	"""
	@staticmethod
	def get_by_identifier(identifier):
		station = memcache.get("station_" + identifier)
		if station is not None:
			logging.info("Station %s found in memcache" % (identifier))
			return station
		else:
			station = Station.all().filter("identifier", identifier).get()
			if station is not None:
				memcache.add("station_" + identifier, station)
				logging.info("Station %s added to memcache" % (identifier))
				return station
			else
				return None
	
	"""
		identifier: str
		return: db.Model > Contribution (0 à 10)
	"""
	@staticmethod
	def get_contributions(identifier):
		contributions = memcache.get("contributions_station_" + identifier)
		if contributions is not None:
			logging.info("Contributions %s found in memcache" % (identifier))
			return contributions
		else:
			contributions = Contribution.all().filter("identifier", identifier).fetch(10)
			if contributions is not None:
				memcache.add("contributions_station_" + identifier, contributions)
				logging.info("Contributions in station %s added to memcache" % (identifier))
				return contributions
			else
				return None
			
	
	