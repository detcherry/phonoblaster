from google.appengine.api import memcache
from google.appengine.ext import db
import random

class GeneralCounterShardConfig(db.Model):
	"""Tracks the number of shards for each named counter."""
	name = db.StringProperty(required=True)
	num_shards = db.IntegerProperty(required=True, default=20)
	
	@staticmethod
	def get_count(name):
	    """Retrieve the value for a given sharded counter.

	    Parameters:
	      name - The name of the counter
	    """
	    total = memcache.get(name)
	    if total is None:
	        total = 0
	        for counter in GeneralCounterShard.all().filter('name = ', name):
	            total += counter.count
	        memcache.add(name, total, 60)
	    return total
	
	@staticmethod
	def init(name, num):
		"""Put an already existing value when creating a counter
		
		Parameters:
		  name - The name of the counter
		  num - The initialization value of this counter
		"""
		config = GeneralCounterShardConfig.get_or_insert(name, name=name)
		def txn():
			index = 0
			shard_name = name + str(index)
			counter = GeneralCounterShard.get_by_key_name(shard_name)
			if counter is None:
				counter = GeneralCounterShard(key_name=shard_name, name=name)
			counter.count = num
			counter.put()
		db.run_in_transaction(txn)
		memcache.set(name, num)
	
	@staticmethod
	def bulk_increment(name, value):
	    """Increment the value for a given sharded counter.

	    Parameters:
	      name - The name of the counter
		  value - The value to add to the counter
	    """
	    config = GeneralCounterShardConfig.get_or_insert(name, name=name)
	    def txn():
		    index = random.randint(0, config.num_shards - 1)
		    shard_name = name + str(index)
		    counter = GeneralCounterShard.get_by_key_name(shard_name)
		    if counter is None:
			    counter = GeneralCounterShard(key_name=shard_name, name=name)
		    counter.count += int(value)
		    counter.put()
	    db.run_in_transaction(txn)
	    memcache.incr(name)
	
	@staticmethod
	def decrement(name):
	    """Decrement the value for a given sharded counter.

	    Parameters:
	      name - The name of the counter
	    """
	    config = GeneralCounterShardConfig.get_or_insert(name, name=name)
	    def txn():
	        index = random.randint(0, config.num_shards - 1)
	        shard_name = name + str(index)
	        counter = GeneralCounterShard.get_by_key_name(shard_name)
	        if counter is None:
	            counter = GeneralCounterShard(key_name=shard_name, name=name)
	        counter.count -= 1
	        counter.put()
	    db.run_in_transaction(txn)
	    memcache.decr(name)		
	
	@staticmethod
	def increase_shards(name, num):
	    """Increase the number of shards for a given sharded counter.
	    Will never decrease the number of shards.

	    Parameters:
	      name - The name of the counter
	      num - How many shards to use

	    """
	    config = GeneralCounterShardConfig.get_or_insert(name, name=name)
	    def txn():
	        if config.num_shards < num:
	            config.num_shards = num
	            config.put()
	    db.run_in_transaction(txn)


class GeneralCounterShard(db.Model):
    """Shards for each named counter"""
    name = db.StringProperty(required=True)
    count = db.IntegerProperty(required=True, default=0)








