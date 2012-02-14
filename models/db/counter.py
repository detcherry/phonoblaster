import random
import os

from google.appengine.api import memcache
from google.appengine.ext import db

class Shard(db.Model):
	num = db.IntegerProperty(required=True, default=20)
	
	@staticmethod
	def get_count(name):
		memcache_name = os.environ["CURRENT_VERSION_ID"] + "." + name
		total = memcache.get(memcache_name)
		if total is None:
			total = 0
			for counter in Counter.all().filter('name = ', name):
				total += counter.count
			memcache.add(memcache_name, total)
		return total

	@staticmethod
	def increment(name):
		shard = Shard.get_or_insert(name)
		def txn():
			index = random.randint(0, shard.num - 1)
			counter_name = name + str(index)
			counter = Counter.get_by_key_name(counter_name)
			if counter is None:
				counter = Counter(key_name=counter_name, name=name)
			counter.count += 1
			counter.put()
		db.run_in_transaction(txn)
		
		memcache_name = os.environ["CURRENT_VERSION_ID"] + "." + name
		memcache.incr(memcache_name)

	@staticmethod
	def decrement(name):
		shard = Shard.get_or_insert(name)
		def txn():
			index = random.randint(0, shard.num - 1)
			counter_name = name + str(index)
			counter = Counter.get_by_key_name(counter_name)
			if counter is None:
				counter = Counter(key_name=counter_name, name=name)
			counter.count -= 1
			counter.put()
		db.run_in_transaction(txn)
		
		memcache_name = os.environ["CURRENT_VERSION_ID"] + "." + name
		memcache.decr(memcache_name)		
	

class Counter(db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True, default=0)
	
	