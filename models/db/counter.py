import random

from google.appengine.api import memcache
from google.appengine.ext import db

class Shard(db.Model):
	name = db.StringProperty(required=True)
	num = db.IntegerProperty(required=True, default=20)
	
	@staticmethod
	def get_count(name):
	    total = memcache.get(name)
	    if total is None:
	        total = 0
	        for counter in Counter.all().filter('name = ', name):
	            total += counter.count
	        memcache.add(name, total)
	    return total

	@staticmethod
	def increment(name):
	    shard = Shard.get_or_insert(name, name=name)
	    def txn():
		    index = random.randint(0, shard.num - 1)
		    counter_name = name + str(index)
		    counter = Counter.get_by_key_name(counter_name)
		    if counter is None:
			    counter = Counter(key_name=counter_name, name=name)
		    counter.count += 1
		    counter.put()
	    db.run_in_transaction(txn)
	    memcache.incr(name)

	@staticmethod
	def decrement(name):
	    shard = Shard.get_or_insert(name, name=name)
	    def txn():
		    index = random.randint(0, shard.num - 1)
		    counter_name = name + str(index)
		    counter = Counter.get_by_key_name(counter_name)
		    if counter is None:
			    counter = Counter(key_name=counter_name, name=name)
		    counter.count -= 1
		    counter.put()
	    db.run_in_transaction(txn)
	    memcache.decr(name)		
	

class Counter(db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True, default=0)
	
	